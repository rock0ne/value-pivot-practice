package main

import "fmt"

func main() {
	readings := []Reading{{"M-1001", 5120}, {"M-1002", 4870}, {"M-1003", -3}}
	for _, r := range readings {
		err := Accept(r)
		fmt.Printf("%s %d Wh: err != nil is %v (%T)\n", r.Meter, r.Wh, err != nil, err)
	}
	var polled []string
	for _, job := range PollJobs([]string{"M-1001", "M-1002", "M-1003"}, func(m string) { polled = append(polled, m) }) {
		job()
	}
	fmt.Println("polled:", polled)
}
