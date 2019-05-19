package main

import (
	"fmt"
	"io"
	"log"
	"os"
)

// Greeting represents a polite word or sign //r TYPE
// of welcome or recognition. //r TYPE
type Greeting struct { //r TYPE
	Salutation string //r TYPE stage=1,2 inline:2="Example: \"Hi\""
	Who        string //r TYPE stage=1,3 inline:3="Greeting recipient"
} //r TYPE

// WriteTo writes the greeting to w. //r WRITETO
func (g Greeting) WriteTo(w io.Writer) (int64, error) { //r WRITETO
	n, err := fmt.Fprintf(w, "%s, %s!\n", //r WRITETO
		g.Salutation, g.Who) //r WRITETO
	return int64(n), err //r WRITETO stage=1,2 inline:2="Why int64?"
} //r WRITETO

func main() { //r MAIN
	g := Greeting{ //r MAIN
		Salutation: "Hello", //r MAIN stage=1,3 inline:3="So configurable"
		Who:        "World", //r MAIN stage=1,3 inline:3="Much wow"
	} //r MAIN
	if _, err := g.WriteTo(os.Stdout); err != nil { //r MAIN
		log.Fatal(err) //r MAIN stage=1,2 inline:2="Always handle errors"
	} //r MAIN
} //r MAIN
