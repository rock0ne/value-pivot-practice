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
	if e == nil {
		return "<no reason>"
	}
	return fmt.Sprintf("meter %s: %s", e.Meter, e.Reason)
}

// Accept validates a reading. A nil error means the reading is stored.
func Accept(r Reading) error {
	var rej *RejectError
	if r.Meter == "" {
		rej = &RejectError{r.Meter, "missing meter ID"}
	}
	if r.Wh < 0 {
		rej = &RejectError{r.Meter, "negative reading"}
	}
	return rej
}
