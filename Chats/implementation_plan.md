# Implementation Plan - Multi-Client Socket Communication System

The objective is to build a robust, low-level socket-based communication system between a centralized server and multiple independent clients. The system will feature a GUI for both server monitoring and client interaction, adhering strictly to TCP/UDP protocols without high-level abstractions.

## User Review Required

> [!IMPORTANT]
> **Technology Stack**: I am proposing **Python** with the built-in `socket` and `threading` modules for communication, and `tkinter` for the GUI. This ensures broad compatibility and strictly low-level interaction as requested.
> **Network Protocol**: I will implement **TCP** (Transmission Control Protocol) to ensure reliable request/response cycles and sequential message delivery, which is ideal for "string-based commands".

## Proposed Changes

The project will be organized into two main standalone applications and a shared configuration module.

### [NEW] Shared Configuration (`config.py`)
Centralized constants to ensure both server and client use the same network parameters.
- `HOST`: Defaulting to `127.0.0.1` (localhost).
- `PORT`: Defaulting to `8080`.
- `BUFFER_SIZE`: Power of 2 (e.g., 1024 or 2048).

### [NEW] Server Application (`server.py`)
The hub of the system.
- **Server Engine**: Uses `socket.socket(socket.AF_INET, socket.SOCK_STREAM)` for TCP.
- **Multi-threading**: Spawns a new daemon thread for every accepted client to handle concurrent requests without blocking the GUI.
- **GUI Dashboard**:
    - Status Indicator: Shows if the server is "Listening" or "Stopped".
    - Client Counter: Real-time count of active socket connections.
    - Activity Log: A scrolling `ScrolledText` widget for connection/message events.

### [NEW] Client Application (`client.py`)
Independent program for end-users.
- **Client Engine**: Connects to the server's host/port.
- **Interactive GUI**:
    - Input: `Entry` field for messages.
    - Action: "Send" button that triggers a socket write.
    - Output: Read-only `Text` area for server responses.

---

## Phase 1: Networking Core & Protocol Definition
Establish the raw communication layer before adding GUI complexity.
1.  Initialize Python scripts and define the `config.py`.
2.  Implement the `SocketServer` class:
    - `bind()` and `listen()`.
    - `accept_connections()` loop in a separate thread.
    - `handle_client(conn, addr)` method to read incoming data and send replies.
3.  Implement the `SocketClient` class:
    - `connect_to_server()`.
    - `send_message(text)` and `receive_response()`.

## Phase 2: GUI Component Development
Build the visual layout for both applications.
1.  **Server UI**:
    - Create the main `Tk` window.
    - Implement the log panel (Activity Monitor).
    - Add control buttons (Start/Stop).
2.  **Client UI**:
    - Create the main `Tk` window.
    - Implement the input field and "Send" button.
    - Implement the response display panel.

## Phase 3: Event Binding & Integration
Wire the networking logic into the GUI.
1.  **Server Integration**:
    - Update the log panel whenever a client connects/disconnects.
    - Log every received request and sent response.
    - Handle `ConnectionResetError` gracefully if a client disconnects unexpectedly.
2.  **Client Integration**:
    - Update the output display when the server responds.
    - Validate inputs (prevent empty messages).

## Phase 4: Validation & Stress Testing
Verify system requirements.
1.  **Concurrency Check**: Launch 3 instances of `client.py` and verify names appear in the Server Log.
2.  **Isolation Check**: Ensure Client A only sees responses intended for Client A.
3.  **Stability Check**: Close clients and verify the server count decrements correctly.

## Open Questions

> [!NOTE]
> 1. **Response Logic**: Should the server return static responses (e.g., "Received: [Message]") or perform specific logic based on commands?
> 2. **Library Preference**: Are you comfortable with `tkinter`? It is standard and requires no install, but we could use `PyQt5` or `CustomTkinter` if you prefer a more modern/premium look.

## Verification Plan

### Manual Verification
1.  Run `python server.py`. Confirm GUI shows "Server Listening...".
2.  Run `python client.py` (Instance 1). Confirm Server Log shows "Client connected from [IP]".
3.  Run `python client.py` (Instance 2). Confirm Server Log count updates to 2.
4.  Send "Hello World" from Instance 1. Confirm Server Log shows receipt and Instance 1 UI shows response.
5.  Close Instance 1. Confirm Server Log shows "Client disconnected".
