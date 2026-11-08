//! Client-approved native NEAR payments for a single ReelOS studio.
use near_sdk::{
    env, json_types::U64, near, require, store::LookupMap, AccountId, Gas, NearToken,
    PanicOnDefault, Promise, PromiseError,
};

pub const STORAGE_FEE: u128 = 20_000_000_000_000_000_000_000;
const HOUR: u64 = 3_600_000_000_000;

#[near(serializers = [json, borsh])]
#[derive(Clone, Debug, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum Status {
    Funded,
    Delivered,
    Paying,
    Paid,
    Refunding,
    Refunded,
}

#[near(serializers = [json, borsh])]
#[derive(Clone)]
pub struct Job {
    pub client: AccountId,
    pub amount: NearToken,
    pub brief_hash: String,
    pub delivery_hash: Option<String>,
    pub deadline_ns: U64,
    pub status: Status,
}

#[near(serializers = [json])]
pub struct Config {
    pub provider: AccountId,
    pub price: NearToken,
    pub storage_fee: NearToken,
}

#[near(contract_state)]
#[derive(PanicOnDefault)]
pub struct Escrow {
    provider: AccountId,
    price: NearToken,
    jobs: LookupMap<String, Job>,
}

#[near]
impl Escrow {
    #[init]
    #[private]
    pub fn new(provider: AccountId, price: NearToken) -> Self {
        require!(price.as_yoctonear() > 0, "Price must be positive");
        require!(
            provider != env::current_account_id(),
            "Use a separate provider account"
        );
        Self {
            provider,
            price,
            jobs: LookupMap::new(b"j"),
        }
    }

    pub fn get_config(&self) -> Config {
        Config {
            provider: self.provider.clone(),
            price: self.price,
            storage_fee: NearToken::from_yoctonear(STORAGE_FEE),
        }
    }

    pub fn get_job(&self, job_id: String) -> Option<Job> {
        self.jobs.get(&job_id).cloned()
    }

    #[payable]
    pub fn fund_job(&mut self, job_id: String, brief_hash: String, deadline_ns: U64) -> Job {
        require!(hex(&job_id, 32), "Invalid job id");
        require!(hex(&brief_hash, 64), "Invalid brief hash");
        require!(!self.jobs.contains_key(&job_id), "Job already exists");
        let now = env::block_timestamp();
        require!(
            deadline_ns.0.saturating_sub(now) >= HOUR
                && deadline_ns.0.saturating_sub(now) <= 7 * 24 * HOUR,
            "Invalid deadline"
        );
        let deposit = self
            .price
            .as_yoctonear()
            .checked_add(STORAGE_FEE)
            .expect("Price overflow");
        require!(
            env::attached_deposit().as_yoctonear() == deposit,
            "Exact price plus storage fee required"
        );
        let job = Job {
            client: env::predecessor_account_id(),
            amount: self.price,
            brief_hash,
            delivery_hash: None,
            deadline_ns,
            status: Status::Funded,
        };
        let before = env::storage_usage();
        self.jobs.insert(job_id.clone(), job.clone());
        self.jobs.flush();
        // Include room for a delivery digest and longer status before taking any funds.
        let bytes = env::storage_usage().saturating_sub(before) + 256;
        require!(
            u128::from(bytes) * env::storage_byte_cost().as_yoctonear() <= STORAGE_FEE,
            "Storage fee insufficient"
        );
        event("funded", &job_id);
        job
    }

    pub fn deliver_job(&mut self, job_id: String, delivery_hash: String) -> Job {
        require!(
            env::predecessor_account_id() == self.provider,
            "Only provider"
        );
        require!(hex(&delivery_hash, 64), "Invalid delivery hash");
        let job = self.jobs.get_mut(&job_id).expect("Job not found");
        require!(job.status == Status::Funded, "Job not funded");
        require!(
            env::block_timestamp() < job.deadline_ns.0,
            "Deadline reached"
        );
        job.delivery_hash = Some(delivery_hash);
        job.status = Status::Delivered;
        event("delivered", &job_id);
        job.clone()
    }

    pub fn approve_job(&mut self, job_id: String) -> Promise {
        let job = self.jobs.get_mut(&job_id).expect("Job not found");
        require!(env::predecessor_account_id() == job.client, "Only client");
        require!(job.status == Status::Delivered, "Job not delivered");
        require!(
            env::block_timestamp() < job.deadline_ns.0,
            "Deadline reached"
        );
        job.status = Status::Paying;
        let amount = job.amount;
        event("paying", &job_id);
        transfer(self.provider.clone(), amount, job_id)
    }

    pub fn refund_job(&mut self, job_id: String) -> Promise {
        let job = self.jobs.get_mut(&job_id).expect("Job not found");
        require!(env::predecessor_account_id() == job.client, "Only client");
        require!(
            matches!(job.status, Status::Funded | Status::Delivered),
            "Job not refundable"
        );
        require!(
            env::block_timestamp() >= job.deadline_ns.0,
            "Deadline not reached"
        );
        job.status = Status::Refunding;
        let (client, amount) = (job.client.clone(), job.amount);
        event("refunding", &job_id);
        transfer(client, amount, job_id)
    }

    #[private]
    pub fn on_transfer(
        &mut self,
        job_id: String,
        #[callback_result] result: Result<(), PromiseError>,
    ) -> bool {
        require!(
            env::predecessor_account_id() == env::current_account_id(),
            "Private callback"
        );
        let job = self.jobs.get_mut(&job_id).expect("Job not found");
        require!(
            matches!(job.status, Status::Paying | Status::Refunding),
            "No pending transfer"
        );
        job.status = match (&job.status, result.is_ok()) {
            (Status::Paying, true) => Status::Paid,
            (Status::Refunding, true) => Status::Refunded,
            (_, false) if job.delivery_hash.is_some() => Status::Delivered,
            _ => Status::Funded,
        };
        event(
            if result.is_ok() {
                "transfer_succeeded"
            } else {
                "transfer_failed"
            },
            &job_id,
        );
        result.is_ok()
    }
}

fn hex(value: &str, length: usize) -> bool {
    value.len() == length
        && value
            .bytes()
            .all(|c| c.is_ascii_digit() || (b'a'..=b'f').contains(&c))
}

fn transfer(receiver: AccountId, amount: NearToken, job_id: String) -> Promise {
    Promise::new(receiver).transfer(amount).then(
        Promise::new(env::current_account_id()).function_call(
            "on_transfer",
            near_sdk::serde_json::to_vec(&near_sdk::serde_json::json!({ "job_id": job_id }))
                .expect("Serialize callback"),
            NearToken::from_yoctonear(0),
            Gas::from_tgas(15),
        ),
    )
}

fn event(action: &str, job_id: &str) {
    env::log_str(
        &near_sdk::serde_json::json!({
            "standard": "reelos_escrow", "version": "1.0.0", "event": action,
            "data": [{ "job_id": job_id }]
        })
        .to_string(),
    );
}
