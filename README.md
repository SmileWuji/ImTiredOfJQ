# Introduction

JSON Structure Preserving Filtering (jspf) tool is a JSON filtering tool similar
to JQ. The intention of this tool is to avoid the learning curve of JQ and have
a tool closer to grep / egrep, so users will not be frustrated to write a
complicated JQ (and which is is yet to be working as expected).

# Specification

The input of the filtering tool will be a stream of JSON documents deliminated
by arbitrary many white space characters, and the output will be the filtered
JSON documents, also deliminated by arbitrary many white space characters. 

```txt
. - this is called the navigation operator which will "navigate" into an object
or a JSON list 

$ - this is called the value operator which will select the value

^ - this is called the root operator which will select the root

// - these are called the regular expression operator; they are used to 
enclose regular expressions

[] {} - these are called the exact matching operator; they are used to enclose
exact strings or specify list ranges or indicies

<> - these are result select operator, much like the group 0 of a REGEX and 
there can only be one result select operator used for each JSON filter

() - these are capturing groups operator for group 1 onward, much like the ones
in REGEX

(?!) (?=) - these are non-capturing groups operator like the ones in regex

? * + - these are the quantifiers

| - this is the OR operator much like the ones in a REGEX
```

The filter can be defined recursively:

Base case:

```txt
.

$ (note: for any filter the value operator can only be used once and it must be
    at the end)

^ (note: for any filter the root operator can only be used once and it must be
    at the beginning)
```

Recursive definition: Given valid filters F_1 F_2

```txt
F_1[S]
F_1[S]?
F_1[S]*
F_1[S]+
    where S is a string token



F_1{I}
F_1{I}?
F_1{I}*
F_1{I}+
    where I is an interval token

F_1/R/
F_1/R/?
F_1/R/*
F_1/R/+
    where R is a regex token

(F_1)
(F_1)?
(F_1)*
(F_1)+

<F_1>
F_1<F_2>
<F_1>F_2
    even though the result select operator can only be used once in any filter
```

The interval token will consist of a sorted list of numbers deliminated by comma
and with a special symbol `...` indicating ranges, and arbitraily white space
without any literal meaning.

For example, `{-5, ..., 5, 10, 15, ...}` will represent the interval
`[-5,5] u {5, 10} u [15, INF)` .

## Samples

```txt
./foo/.*./bar/$/123.*/
```

This expression will filter all of the below JSON objects.

```json
{"foo": {"bar": "123456"}}
```

```json
{"foo": [0, {"bar": "123456"}]}
```


```json
{"foo": {"blahblahblah": {"bar": "123456"}}}
```

```json
{"some_other_root": {"foo": {"bar": "123999"}}}
```

```json
{"some_other_root_with_container": [{"foo": {"bar": "123999"}}]}
```

As we can see, no matter what the JSON looks like, if any part of the JSON can
match pattern, then the whole matching JSON will pass the filter. This behaviour
can be controlled by specifying the result select operator.

# Development

Dependency:
* python 3.6+
    * pytest
* GNU make

To bootstrap this project for the very first time, please run `make dependency`.

To build this project for testing, please run `make` or `make test`.
