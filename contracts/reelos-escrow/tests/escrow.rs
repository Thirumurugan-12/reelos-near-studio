use near_sdk::{
    json_types::U64,
    test_utils::{accounts, get_created_receipts, VMContextBuilder},
    testing_env, NearToken, PromiseError,
};
use reelos_escrow::{Escrow, Status, STORAGE_FEE};

const PRICE: u128 = 100_000_000_000_000_000_000_000;
const DEADLINE: u64 = 3_600_000_000_001;
fn id() -> String {
    "a".repeat(32)
}
fn hash() -> String {
    "b".repeat(64)
}
fn context(who: usize, deposit: u128, time: u64) {
    let mut b = VMContextBuilder::new();
    b.current_account_id(accounts(0))
        .predecessor_account_id(accounts(who))
        .attached_deposit(NearToken::from_yoctonear(deposit))
        .block_timestamp(time)
        .account_balance(NearToken::from_near(100));
    testing_env!(b.build());
}
fn funded() -> Escrow {
    context(0, 0, 1);
    let mut e = Escrow::new(accounts(1), NearToken::from_yoctonear(PRICE));
    context(2, PRICE + STORAGE_FEE, 1);
    e.fund_job(id(), hash(), U64(DEADLINE));
    e
}
fn delivered() -> Escrow {
    let mut e = funded();
    context(1, 0, 2);
    e.deliver_job(id(), hash());
    e
}
#[test]
fn funding_records_client_and_keeps_storage_separate() {
    let e = funded();
    let j = e.get_job(id()).unwrap();
    assert_eq!(j.client, accounts(2));
    assert_eq!(j.amount.as_yoctonear(), PRICE);
    assert_eq!(j.status, Status::Funded);
}
#[test]
fn approval_only_settles_after_transfer_callback() {
    let mut e = delivered();
    context(2, 0, 3);
    let _ = e.approve_job(id());
    assert_eq!(e.get_job(id()).unwrap().status, Status::Paying);
    assert!(!get_created_receipts().is_empty());
    context(0, 0, 4);
    assert!(e.on_transfer(id(), Ok(())));
    assert_eq!(e.get_job(id()).unwrap().status, Status::Paid);
}
#[test]
fn failed_payment_can_be_retried() {
    let mut e = delivered();
    context(2, 0, 3);
    let _ = e.approve_job(id());
    context(0, 0, 4);
    assert!(!e.on_transfer(id(), Err(PromiseError::Failed)));
    assert_eq!(e.get_job(id()).unwrap().status, Status::Delivered);
    context(2, 0, 5);
    let _ = e.approve_job(id());
}
#[test]
fn deadline_refunds_unapproved_delivery() {
    let mut e = delivered();
    context(2, 0, DEADLINE);
    let _ = e.refund_job(id());
    assert_eq!(e.get_job(id()).unwrap().status, Status::Refunding);
    context(0, 0, DEADLINE);
    assert!(e.on_transfer(id(), Ok(())));
    assert_eq!(e.get_job(id()).unwrap().status, Status::Refunded);
}
#[test]
fn failed_refund_restores_delivery() {
    let mut e = delivered();
    context(2, 0, DEADLINE);
    let _ = e.refund_job(id());
    context(0, 0, DEADLINE);
    e.on_transfer(id(), Err(PromiseError::Failed));
    assert_eq!(e.get_job(id()).unwrap().status, Status::Delivered);
}
#[test]
fn failed_refund_restores_undelivered_job() {
    let mut e = funded();
    context(2, 0, DEADLINE);
    let _ = e.refund_job(id());
    context(0, 0, DEADLINE);
    e.on_transfer(id(), Err(PromiseError::Failed));
    assert_eq!(e.get_job(id()).unwrap().status, Status::Funded);
}
#[test]
#[should_panic(expected = "Only provider")]
fn stranger_cannot_deliver() {
    let mut e = funded();
    context(3, 0, 2);
    e.deliver_job(id(), hash());
}
#[test]
#[should_panic(expected = "Only client")]
fn provider_cannot_release_funds() {
    let mut e = delivered();
    context(1, 0, 3);
    let _ = e.approve_job(id());
}
#[test]
#[should_panic(expected = "Only client")]
fn stranger_cannot_refund() {
    let mut e = funded();
    context(3, 0, DEADLINE);
    let _ = e.refund_job(id());
}
#[test]
#[should_panic(expected = "Deadline not reached")]
fn early_refund_rejected() {
    let mut e = funded();
    context(2, 0, 2);
    let _ = e.refund_job(id());
}
#[test]
#[should_panic(expected = "Job already exists")]
fn duplicate_funding_rejected() {
    let mut e = funded();
    e.fund_job(id(), hash(), U64(DEADLINE));
}
#[test]
#[should_panic(expected = "Exact price plus storage fee required")]
fn wrong_deposit_rejected() {
    let mut e = funded();
    context(2, PRICE, 1);
    e.fund_job("c".repeat(32), hash(), U64(DEADLINE));
}
#[test]
#[should_panic(expected = "Job not delivered")]
fn cannot_pay_before_delivery() {
    let mut e = funded();
    context(2, 0, 3);
    let _ = e.approve_job(id());
}
#[test]
#[should_panic(expected = "Job not delivered")]
fn cannot_pay_twice_while_pending() {
    let mut e = delivered();
    context(2, 0, 3);
    let _ = e.approve_job(id());
    let _ = e.approve_job(id());
}
#[test]
#[should_panic(expected = "Job not refundable")]
fn cannot_refund_pending_payment() {
    let mut e = delivered();
    context(2, 0, 3);
    let _ = e.approve_job(id());
    context(2, 0, DEADLINE);
    let _ = e.refund_job(id());
}
#[test]
#[should_panic(expected = "Deadline reached")]
fn late_delivery_rejected() {
    let mut e = funded();
    context(1, 0, DEADLINE);
    e.deliver_job(id(), hash());
}
#[test]
#[should_panic(expected = "Deadline reached")]
fn late_approval_rejected() {
    let mut e = delivered();
    context(2, 0, DEADLINE);
    let _ = e.approve_job(id());
}
#[test]
#[should_panic(expected = "Private callback")]
fn stranger_cannot_forge_callback() {
    let mut e = delivered();
    context(2, 0, 3);
    let _ = e.approve_job(id());
    context(3, 0, 4);
    e.on_transfer(id(), Ok(()));
}
#[test]
#[should_panic(expected = "Invalid brief hash")]
fn invalid_hash_rejected() {
    let mut e = funded();
    context(2, PRICE + STORAGE_FEE, 1);
    e.fund_job("c".repeat(32), "secret footage".into(), U64(DEADLINE));
}
#[test]
#[should_panic(expected = "Invalid deadline")]
fn too_short_deadline_rejected() {
    let mut e = funded();
    context(2, PRICE + STORAGE_FEE, 1);
    e.fund_job("c".repeat(32), hash(), U64(10));
}

fn assert_transfer_to(who: usize) {
    let receipts = get_created_receipts();
    let transfers: Vec<_> = receipts
        .iter()
        .flat_map(|r| {
            r.actions.iter().filter_map(|a| {
                if let near_sdk::mock::MockAction::Transfer { deposit, .. } = a {
                    Some((r.receiver_id.clone(), deposit.as_yoctonear()))
                } else {
                    None
                }
            })
        })
        .collect();
    assert_eq!(transfers, vec![(accounts(who), PRICE)]);
    let callback = receipts
        .iter()
        .find(|r| r.receiver_id == accounts(0))
        .unwrap();
    assert!(callback.actions.iter().any(|a| matches!(a,
        near_sdk::mock::MockAction::FunctionCallWeight { method_name, args, .. }
        if method_name == b"on_transfer" && near_sdk::serde_json::from_slice::<near_sdk::serde_json::Value>(args).unwrap()["job_id"] == id()
    )));
}
#[test]
fn payout_sends_price_to_provider_and_retains_storage() {
    let mut e = delivered();
    context(2, 0, 3);
    drop(e.approve_job(id()));
    assert_transfer_to(1);
}
#[test]
fn refund_sends_price_to_client_and_retains_storage() {
    let mut e = funded();
    context(2, 0, DEADLINE);
    drop(e.refund_job(id()));
    assert_transfer_to(2);
}
#[test]
#[should_panic(expected = "Job not refundable")]
fn paid_job_cannot_be_refunded() {
    let mut e = delivered();
    context(2, 0, 3);
    drop(e.approve_job(id()));
    context(0, 0, 4);
    e.on_transfer(id(), Ok(()));
    context(2, 0, DEADLINE);
    drop(e.refund_job(id()));
}
#[test]
#[should_panic(expected = "Job not refundable")]
fn refunded_job_cannot_refund_twice() {
    let mut e = funded();
    context(2, 0, DEADLINE);
    drop(e.refund_job(id()));
    context(0, 0, DEADLINE);
    e.on_transfer(id(), Ok(()));
    context(2, 0, DEADLINE);
    drop(e.refund_job(id()));
}
#[test]
#[should_panic(expected = "Invalid job id")]
fn arbitrary_job_ids_rejected() {
    let mut e = funded();
    context(2, PRICE + STORAGE_FEE, 1);
    e.fund_job("../../private".into(), hash(), U64(DEADLINE));
}
#[test]
#[should_panic(expected = "Invalid delivery hash")]
fn private_preview_url_cannot_be_used_as_delivery_hash() {
    let mut e = funded();
    context(1, 0, 2);
    e.deliver_job(id(), "https://private.example/video.mp4".into());
}

fn factory_context(parent: &str) {
    let mut b = VMContextBuilder::new();
    b.current_account_id("escrow.studio.testnet".parse().unwrap())
        .predecessor_account_id(parent.parse().unwrap());
    testing_env!(b.build());
}
#[test]
fn parent_initializes_a_keyless_studio_escrow() {
    factory_context("studio.testnet");
    let e = Escrow::new_for_studio(NearToken::from_yoctonear(PRICE));
    assert_eq!(e.get_config().provider.as_str(), "studio.testnet");
}
#[test]
#[should_panic(expected = "Only the escrow account's parent")]
fn stranger_cannot_initialize_a_studio_escrow() {
    factory_context("stranger.testnet");
    Escrow::new_for_studio(NearToken::from_yoctonear(PRICE));
}
