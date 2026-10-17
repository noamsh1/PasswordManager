Password Manager
-
A secure python Password Manager application. Allows you to keep all your password in one place, and generate long and secure passwords without the risk of forgetting them.

features:
- Server with multi-client connections (using sockets). Includes end to end encryption.
- encrypted and secure Database.
- Nice looking customtkinter GUI.
- Multi factor authentication
  - Username and password
  - One-time code sent to email.
  - Biometric authentication: face and voice recognition.
- Secure password generation system for users' registered sites.
- Defense against DoS attacks and brute force in login.
- "I forgot my password" mechanism for the application login.

Under Releases, there are the server and client zips for download.

To run the server, extract the server folder from the zip, and simply double click on server.exe.

To run the client, open the client directory in the terminal, and run this command: client.exe "{server IP}" (Replace {server IP} with the server's IP address). If the server is running on your local machine, you can simply double click on client.exe since it automatically connects to localhost if no IP is provided.

*For a much more detailed documentation of the project in Hebrew, go to Doc/Password Manager doc.pdf.
