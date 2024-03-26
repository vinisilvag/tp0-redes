# Basic UDP Authentication Token Generator

## Introduction

In this assignment we will develop an authenticator of student groups. The authentication protocol is capable of authenticating students individually or in groups. We will use the authenticator in the follow-up assignments.

## Objectives

- Introduce the socket programming interface
- Introduce the concepts of client and server applications
- Introduce the concepts of data encoding and transmission

## Implementation

This programming assignment can be implemented in any programming language, but using the low-level POSIX socket interface. Although the POSIX interface is the simplest available, it is also the "common denominator" when it comes to network applications. By using the POSIX interface we will get a glimpse of the foundations under more advanced libraries and frameworks.

> In Python, the POSIX socket interface is that of the [`socket`](https://docs.python.org/3/library/socket.html) module. This module should be enough for all network communications in this assignment. In C, the POSIX socket interface is in the [`socket.h`](https://man7.org/linux/man-pages/man7/socket.7.html) header and friends. In Java the closest to the POSIX interface is the [`java.net.Socket`](https://docs.oracle.com/javase/7/docs/api/java/net/Socket.html) interface and the [`ServerSocket`](https://docs.oracle.com/javase/7/docs/api/java/net/ServerSocket.html) class.

## Protocol

The authentication protocol used in this assignment is a request-response protocol. The `client` sends a message to the `server` and waits for a response. Authentications are done in at least two steps. First, the `client` requests the `server` an authentication token. Second, after receiving the authentication token, the `client` can authenticate itself infinite times using the token, for example, to access other functionalities in the application.

The communication protocol uses [UDP](https://en.wikipedia.org/wiki/User_Datagram_Protocol) messages. Error detection and message retransmission in case of failure is the responsibility of the client.

> The two common transport protocols on the Internet are TCP (Transmission Control Protocol) and UDP (User Datagram Protocol). We will study them in detail in this course, but for now it suffices to know that TCP implements error and congestion detection, while UDP does not. If the library you are using has a default transport protocol, it is likely TCP; in this case set the transport protocol to UDP manually.

The protocol transmits data in binary form. All _integers_ transferred by the protocol should be encoded in [network byte order](https://en.wikipedia.org/wiki/Endianness#Networking). Each message starts with a 2-byte integer indicating the message type and the semantics of the following bytes is defined for each message type. We next describe the messages in the protocol.

> In Python, use the [`struct`](https://docs.python.org/3/library/struct.html) module to put integers in network byte order. In C, use the [`htonl/ntohl/htons/ntohs`](https://linux.die.net/man/3/htonl) functions (these letters relate to `h`ost/`n`etwork `to` `n`etwork/`h`ost `s`hort/`l`ong depending on the direction of conversion and whether the integer has 2 (short) or 4 bytes (long)).

### Individual Token Request \[1\]

An _individual token request_ is sent by a `client` to the `server` to get an authentication token for one student. The message contains a 2-byte integer with value 1 indicating the _type_, a 12-byte string (in ASCII encoding) containing the student's _ID_, and a 4-byte integer containing the token _nonce_. The nonce can be changed in case the student wants to generate multiple tokens for different uses. In total, a request has 18 bytes as follows:

> In this assignment we will use our NetIDs as our identifier. We should always encode the NetID in 12 characters, filling in any empty characters at the end with spaces. The NetID should be encoded as [ASCII](https://en.wikipedia.org/wiki/ASCII). In Python, you can encode a string as a sequence of bytes using the ASCII encoding using `bytes(string_variable, encoding="ascii")`. In C, strings are encoded in ASCII by default (but note you should _not_ transmit the null-terminating byte).

    0         2                        14                  18
    +----+----+----+----/    /----+----+----+----+----+----+
    | 1       | ID                     | nonce             |
    +----+----+----+----/    /----+----+----+----+----+----+

### Individual Token Response \[2\]

An _individual token response_ is sent by the `server` to the `client` in response to an _individual token request_. The response contains a 2-byte integer with the value 2, the student's _ID_, and the token _nonce_ present in the original request, follows by a 64-byte string containing the authentication token. The authentication token is encoded in hexadecimal and contains only the ASCII characters between `0-9` and `a-f`. An individual token response contains 82 bytes as follows:

    0       2               14              18                    82
    +---+---+---+---/   /---+---+---+---+---+---+---/         /---+
    | 2     | ID            | nonce         | token               |
    +---+---+---+---/   /---+---+---+---+---+---+---/         /---+

The sequence of 80 bytes containing the _ID_ (12 bytes), the _nonce_ (4 bytes), and the token (64 bytes) will be referred to in the following as _student authentication sequence_, or SAS for short.

### Individual Token Validation \[3\]

An _individual token validation_ message is sent by a `client` to the `server` to check if an authentication token is valid. An individual token validation message contains a 2-byte integer with value 3, followed by the 80 bytes of the SAS being verified, as shown below:

    0       2               14              18                    82
    +---+---+---+---/   /---+---+---+---+---+---+---/         /---+
    | 3     | ID            | nonce         | token               |
    +---+---+---+---/   /---+---+---+---+---+---+---/         /---+

### Individual Token Status \[4\]

An _individual token status_ message is sent by the `server` to the `client` in response to an _individual token validation_ message. The individual token status message contains a 2-byte integer with value 4, the 80 bytes of a SAS under validation, and one byte informing the _status_. A status of zero means that the token is valid, and a nonzero status means that the token is invalid. An individual token status message contains 83 bytes as follows:

    0       2               14              18                    82  83
    +---+---+---+---/   /---+---+---+---+---+---+---/         /---+---+
    | 4     | ID            | nonce         | token               | s |
    +---+---+---+---/   /---+---+---+---+---+---+---/         /---+---+

### Group Token Request \[5\]

A _group token request_ is sent by a `client` to the `server`to generate a token that authenticates multiple SAS. One possible use is when programming assignments are developed by groups of students. A group token request contains a 2-byte integer with value 5, a 2-byte integer with the _count_ `N` of SAS in the message, and a sequence of `N` SAS (80 bytes each). The number of SAS in the message (count) should be larger than zero and less than 16 (the number of SAS _can_ be 1). A group token request contains `4 + 80N` bytes, where `N` is the number of SAS, as shown below:

    0       2       4          84         164       4+80N
    +---+---+---+---+--/     /--+--/     /--+--/     /--+
    | 5     | N     | SAS-1     | SAS-2     | SAS-N     |
    +---+---+---+---+--/     /--+--/     /--+--/     /--+

### Group Token Response \[6\]

A _group token response_ is sent by a `server` to a `client` in response to a group token request. The response contains a two-byte integer with value 6, a 2-byte integer with the _count_ `N` of SAS in the request, a sequence of `N` SAS, and a sequence of 64 bytes with the group token. The group token uses the same hexadecimal encoding as the individual token. A group token response contains `4 + 80N + 64` bytes as shown below:

    0       2       4          84         164       4+80N         4+80N+64
    +---+---+---+---+--/    /--+--/     /--+--/     /--+--/   /--+
    | 6     | N     | SAS-1    | SAS-2     | SAS-N     | token   |
    +---+---+---+---+--/    /--+--/     /--+--/     /--+--/   /---

The sequence of `2 + 80N + 64` bytes containing the count of SAS (N), the SAS, and the group token will be referred to below as _group authentication sequence_, or GAS for short. The authenticator is sensitive to the order in which the SAS appear in the GAS. As such, the validation should now change the ordering of SAS.

### Group Token Validation \[7\]

A _group token validation_ message is sent by a `client` to the `server` to check if a token is valid. A group token validation message contains a 2-byte integer with the value 7, follows by the GAS under validation:

    0       2       4          84         164       4+80N         68+80N
    +---+---+---+---+--/     /--+--/     /--+--/     /--+--/   /--+
    | 7     | N     | SAS-1     | SAS-2     | SAS-N     | token   |
    +---+---+---+---+--/     /--+--/     /--+--/     /--+--/   /--+

### Group Token Status \[8\]

A _group token status_ message is sent by the `server` to a `client` in response to a _group token validation_ message. A group token status message contains a 2-byte integer with value 8, the GAS under validation, and 1 byte indicating the _status_. A status of zero means that the token is valid, and a nonzero status means that the token is invalid. A group token status message has `4 + 80N + 64 + 1` bytes, as follows:

    0       2       4          84         164       4+80N    68+80N   69+80N
    +---+---+---+---+--/     /--+--/     /--+--/     /--+--/   /--+---+
    | 8     | N     | SAA-1     | SAA-2     | SAA-N     | token   | s |
    +---+---+---+---+--/     /--+--/     /--+--/     /--+--/   /--+---|

### Error Message \[256\]

An _error message_ is sent by the `server` to the `client` whenever an error is detected in a request. An error message contains a 2-byte integer with the value 256 and another 2-byte integer with an error code, like so:

    0         2         4
    +----+----+----+----+
    | 256     | error   |
    +----+----+----+----+

The following error codes are defined:

- `INVALID_MESSAGE_CODE = 1`, sent when the `client` sent a request with an unknown type (that is, the first 2-byte integer is not recognized).
- `INCORRECT_MESSAGE_LENGTH = 2`, sent when the `client` sent a request whose size is incompatible with the request type.
- `INVALID_PARAMETER = 3`, sent when the `server` detects an error in any field of a request. One example is an invalid value of the SAS count `N` in the group authentication message.
- `INVALID_SINGLE_TOKEN = 4`, sent when one SAS in a GAS is invalid itself. (The server checks the validity of each SAS before generating a token for a group authentication token.)
- `ASCII_DECODE_ERROR = 5`, sent when a message contains a non-ASCII character (whether in the ID or the token).

## Testing

### Authentication Server

We will use the authentication protocol throughout this class to identify students in their programming assignments. The authentication server will run on port UDP/51001. The address of the authentication server will be announced on the course website.

### Command-Line Interface

The `client` program should receive three positional arguments:

    ./client.py <host> <port> <command>

Where `host` and `port` are those for the authentication server above. The `command` parameter specifies which command will be executed. In particular, the program must support the four commands below:

1.  `itr <id> <nonce>`

    This command should send an individual token request to the `server`. The SAS received from the `server` must be printed as the program's output.

2.  `itv <SAS>`

    This command should send an individual token validation message to the `server` for the SAS given on the command line. The validation result must be printed as the program's output.

3.  `gtr <N> <SAS-1> <SAS-2> ... <SAS-N>`

    This command should send a group token request to the `server`. The parameter `N` gives the number of SAS that will be sent to the `server`. The GAS received from the `server` should be printed as the program's output.

4.  `gtv <GAS>`

    This command should send a group token validation message to the `server`. The validation result should be printed as the program's output.

On the command line and program output, SAS and GAS should be informed in a standardized manner, as follows. SAS fields should be separated by a colon (`:`), and be printed as a string:

    <id>:<nonce>:<token>

Similarly, GAS should be printed with the SAS and token separated by a plus sign (`+`). Each SAS should be printed as specified above. For example:

    <SAS1>+<SAS2>+<SAS3>+<token>

Note that there are no spaces in SAS and GAS.

### Example Use

    % ./client.py vcm-23691.vm.duke.edu 51001 itr ifs4 1
    ifs4:1:2c3bb3f0e946a1afde7d9d0c8c818762a6189e842abd8aaaf85c9faac5b784d2

    % ./client.py vcm-23691.vm.duke.edu 51001 itv ifs4:1:2c3bb3f0e946a1afde7d9d0c8c818762a6189e842abd8aaaf85c9faac5b784d2
    0

    # Note the incorrect nonce:
    % ./client.py vcm-23691.vm.duke.edu 51001 itv ifs4:5:2c3bb3f0e946a1afde7d9d0c8c818762a6189e842abd8aaaf85c9faac5b784d2
    1

    # Note the incorrect last two digits of the token:
    % ./client.py vcm-23691.vm.duke.edu 51001 itv ifs4:1:2c3bb3f0e946a1afde7d9d0c8c818762a6189e842abd8aaaf85c9faac5b784ff
    1

    % ./client.py vcm-23691.vm.duke.edu 51001 itr ifs4 2
    ifs4:2:cf87a60a90159078acecca4415c0331939ebb28ac5528322ac03d7c26b140b98

    % ./client.py vcm-23691.vm.duke.edu 51001 gtr 2 ifs4:1:2c3bb3f0e946a1afde7d9d0c8c818762a6189e842abd8aaaf85c9faac5b784d2 ifs4:2:cf87a60a90159078acecca4415c0331939ebb28ac5528322ac03d7c26b140b98
    ifs4:1:2c3bb3f0e946a1afde7d9d0c8c818762a6189e842abd8aaaf85c9faac5b784d2+ifs4:2:cf87a60a90159078acecca4415c0331939ebb28ac5528322ac03d7c26b140b98+e51d06a4174b5385c8daff714827b4b4cb4f93ff1b83af86defee3878c2ae90f

    % ./client.py vcm-23691.vm.duke.edu 51001 gtv ifs4:1:2c3bb3f0e946a1afde7d9d0c8c818762a6189e842abd8aaaf85c9faac5b784d2+ifs4:2:cf87a60a90159078acecca4415c0331939ebb28ac5528322ac03d7c26b140b98+e51d06a4174b5385c8daff714827b4b4cb4f93ff1b83af86defee3878c2ae90f
    0

### Implementation Details

The string containing student IDs and tokens should be encoded using ASCII. IDs should contain only the characters `0-9`, `a-z`, and `A-Z`; tokens should contain only the characters `0-9` and `a-f`.

Implementations should configure a timeout timer to detect communication failures (which are not automatically handled by the UDP transport). In particular, when no response is received from the server, the client should re-send the request.

> In Python, you can set a timeout on a socket by calling the `settimeout` function.

Implementations should accept both IPv4 and IPv6 protocols transparently. That is, the user should not need to worry about which IP version will be used.

> The protocol does not allow a mapping of requests to responses. In other words, if a request is retransmitted and one response is received, the `client` cannot identify which request (the original or the retransmission) was answered. However, this is not an issue in this assignment as a request has only _one_ possible valid response as a SAS token is a function of the ID and the nonce, and a GAS token is a function of its SAS. This allows a `client` to send multiple concurrent requests to the `server` and still handle errors.

## Suggestions

Implement each request/response pair at a time. We suggest you implement the messages in the order presented in this documentation. In the debugging process, consider comparing your encoded messages with those messages encoded by your colleagues to check that they match.

For students implementing the assignment in compiled languages, check how to disable [data structure padding](https://en.wikipedia.org/wiki/Data_structure_alignment), which is often enabled by default. In C, [you can use](https://stackoverflow.com/questions/3318410/pragma-pack-effect) the `#pragma pack` directive for this end:

    struct itr {
        uint16_t type;
        char id[12];
        uint32_t nonce;
    };
    #pragma pack(0)

## Ambiguities and Errors

As with many Internet protocols, the protocol specified in this assignment may be flawed, and the instructor's implementation of the `server` may contain bugs. I don't expect this to happen, but students that identify flaws or bugs will be awarded extra credit depending on the complexity and inconvenience caused by the issue.

## What to Submit and Grading

You should submit your source code and complete at least two validations with a GAS containing your NetID (you can generate a GAS containing only your SAS by setting `N = 1` in the group token request). You should complete one validation using IPv4, and one validation using IPv6.

If you implemented your client in a compiled language, submit documentation with compilation instructions.

The proposed protocol has multiple limitations and is not well suited for authentication in real systems. You should also submit a PDF describing one limitation of the proposed authentication protocol and how it could be exploited in the wild (e.g., to bypass authentication or other misconduct). Two paragraphs should be enough.

## Extra Credit

Extensions to the proposed protocol will be considered for extra credit. Discuss any extension ideas with the instructor.
