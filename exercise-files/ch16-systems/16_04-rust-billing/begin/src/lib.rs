/// Amount due this month, in pence: charges minus the customer's export credit.
pub fn amount_due(charges_p: u32, credit_p: u32) -> u32 {
    charges_p - credit_p
}

/// The storage slot for a gateway channel.
pub fn channel_slot(channel: u32) -> u8 {
    channel as u8
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn due_is_charges_minus_credit() {
        assert_eq!(amount_due(5_000, 1_200), 3_800);
    }

    #[test]
    fn slot_matches_channel() {
        assert_eq!(channel_slot(7), 7);
    }
}
