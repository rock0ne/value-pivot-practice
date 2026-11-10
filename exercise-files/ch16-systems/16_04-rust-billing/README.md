# 16_04: Rust billing: overflow and casts

**Book:** Chapter 16, Rust: the language to watch.

The billing tests pass, but in a release build a customer with £60.20 of solar credit and £41.50 of charges is billed 4294965426 pence, and a reading from channel 260 is stored in slot 4. Make `amount_due` carry unused credit forward instead of wrapping round, make `channel_slot` refuse channels that don't fit, and keep overflow checks on in release builds. You're done when the release run shows 1870 pence carried forward, and Clippy's `cast_possible_truncation` lint finds nothing.

**Files:** `begin/src/lib.rs`, `begin/src/main.rs` and `begin/Cargo.toml` (edit these). The answer is in `end/`: open it only when you've finished, or you're truly stuck.

**Check your work:** from the `ch16-systems` folder, run `python check.py`.

**Hint:** look at `checked_sub` and `u8::try_from`. The release setting goes under `[profile.release]` in `Cargo.toml`.
