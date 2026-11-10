package main

import "testing"

func TestRejectsNegative(t *testing.T) {
	if err := Accept(Reading{"M-1", -1}); err == nil {
		t.Fatal("negative reading accepted")
	}
}

func TestRejectsMissingMeter(t *testing.T) {
	if err := Accept(Reading{"", 10}); err == nil {
		t.Fatal("reading without a meter accepted")
	}
}

func TestPollJobs(t *testing.T) {
	var got []string
	for _, j := range PollJobs([]string{"M-1"}, func(m string) { got = append(got, m) }) {
		j()
	}
	if len(got) != 1 || got[0] != "M-1" {
		t.Fatalf("got %v", got)
	}
}
