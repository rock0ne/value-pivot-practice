use billing::{amount_due, channel_slot};

fn main() {
    let (due, carried) = amount_due(4_150, 6_020);
    println!("amount due: {} pence, credit carried forward: {} pence", due, carried);
    match channel_slot(260) {
        Ok(slot) => println!("reading from channel 260 stored in slot {slot}"),
        Err(e) => println!("reading from channel 260 refused: {e}"),
    }
}
