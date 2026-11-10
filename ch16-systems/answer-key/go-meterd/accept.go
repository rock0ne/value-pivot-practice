package main

import "fmt"

// Reading is one upload from a smart-meter gateway.
type Reading struct {
	Meter string
	Wh    int64
}

// RejectError says why a reading was refused.
type RejectError struct {
	Meter  string
	Reason string
}

func (e *RejectError) Error() string {
	return fmt.Sprintf("meter %s: %s", e.Meter, e.Reason)
}

// Accept validates a reading. A nil error means the reading is stored.
// The fix: return a literal nil on success, never a typed nil pointer.
func Accept(r Reading) error {
	if r.Meter == "" {
		return &RejectError{r.Meter, "missing meter ID"}
	}
	if r.Wh < 0 {
		return &RejectError{r.Meter, "negative reading"}
	}
	return nil
}
