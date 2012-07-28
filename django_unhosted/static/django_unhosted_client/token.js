// `receiveToken` parses the OAuth token from the URL params
var token = remoteStorage.receiveToken();

if (token) {
	// We send the token [back to our main page](tutorial.html)
	window.opener.postMessage(token, location.protocol+'//'+location.host);
}

// and close the window.
window.close();
