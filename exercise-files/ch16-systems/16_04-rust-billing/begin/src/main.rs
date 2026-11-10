use billing::{amount_due, channel_slot};

fn main() {
    // A customer whose solar export credit (£60.20) is more than this month's charges (£41.50).
    let due = amount_due(4_150, 6_020);
    println!("amount due: {} pence (£{}.{:02})", due, due / 100, due % 100);
    println!("reading from channel 260 stored in slot {}", channel_slot(260));
}
