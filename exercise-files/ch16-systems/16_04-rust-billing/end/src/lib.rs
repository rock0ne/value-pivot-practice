/// Amount due this month, in pence, and any credit carried forward.
/// The fix: say what happens when the credit is larger, instead of subtracting blindly.
pub fn amount_due(charges_p: u32, credit_p: u32) -> (u32, u32) {
    match charges_p.checked_sub(credit_p) {
        Some(due) => (due, 0),
        None => (0, credit_p - charges_p),
    }
}

/// The storage slot for a gateway channel, refusing channels that don't fit.
pub fn channel_slot(channel: u32) -> Result<u8, String> {
    u8::try_from(channel).map_err(|_| format!("channel {channel} is out of range for a slot"))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn due_is_charges_minus_credit() {
        assert_eq!(amount_due(5_000, 1_200), (3_800, 0));
    }

    #[test]
    fn credit_larger_than_charges_carries_forward() {
        assert_eq!(amount_due(4_150, 6_020), (0, 1_870));
    }

    #[test]
    fn slot_refuses_large_channel() {
        assert!(channel_slot(260).is_err());
        assert_eq!(channel_slot(7), Ok(7));
    }
}
