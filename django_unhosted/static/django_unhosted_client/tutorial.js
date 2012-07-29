// Accepting remoteStorage accounts in your web app
// ------------------------------------------------

// Get the url from data-receive_token_url on this <script> tag,
//  which can be served from any site-specific path, hence cannot be
//  hard-coded here.
var scripts = document.getElementsByTagName('script');
var receive_token_url = $(scripts[scripts.length-1]).data('receive_token_url');
if (receive_token_url == undefined)
	alert('Failed to determine receive_token_url, authorization requests will fail');

storage = function() {

	// `getStorageInfo` takes a user address ("user@host") and a callback as its
	// arguments. The callback will get an error code, and a `storageInfo`
	// object. If the error code is `null`, then the `storageInfo` object will
	// contain data required to access the remoteStorage.
	function connect(userAddress, callback) {
		remoteStorage.getStorageInfo(userAddress, function(error, storageInfo) {
			if(error) {
				alert('Could not load storage info');
				console.log(error);
			} else {
				console.log('Storage info received:');
				console.log(storageInfo);
			}

			callback(error, storageInfo);
		});
	}

	// Getting data from the "public/tutorial" category doesn't require any credentials.
	// For writing to a user's public data, or reading/writing any of the other
	// categories, we need to do an OAuth request first to obtain a token.

	// This method opens a popup that sends the user to the OAuth dialog of the
	// remoteStorage provider.
	function authorize(scopes) {
		var storageInfo = JSON.parse(localStorage.getItem('userStorageInfo'));
		var redirectUri = location.protocol + '//' + location.host + receive_token_url;

		// `createOAuthAddress` takes the `storageInfo`, the scopes that we
		// intend to access and a redirect URI that the storage provider sends the
		// user back to after authorization.
		// The scope string for read-write access to public 'tutorial' data is 'public/tutorial:rw'
		// The scope string for read-write access to default (private) 'tutorial' data is 'tutorial:rw'
		// That page extracts the token and sends it back to us, which is
		// [described here](token.html).
		var oauthPage = remoteStorage.createOAuthAddress(storageInfo, scopes, redirectUri);
		var popup = window.open(oauthPage);
	}

	// To get the OAuth token we listen for the `message` event from the
	// receive_token.html that sends it back to us.
	window.addEventListener('message', function(event) {
		if(event.origin == location.protocol +'//'+ location.host) {
			console.log('Received an OAuth token: ' + event.data);
			localStorage.setItem('bearerToken', event.data);
			helper.setAuthorizedState(helper.isAuthorized());
		}
	}, false);

	// To get data from the remoteStorage, we need to create a client with
	// the `createClient` method. It takes the object that we got via the
	// `getStorageInfo` call and the category we want to access. If the
	// category is any other than "public", we also have to provide the OAuth
	// token.
	function getData(path, callback) {
		var storageInfo = JSON.parse(localStorage.getItem('userStorageInfo'));
		var client;

		if (path.split('/').length < 2) {
			cb('error: path '+path+' contains no slashes');
			return;
		} else if(path.split('/')[0] == 'public') {
			client = remoteStorage.createClient(storageInfo, '');
		} else {
			var token = localStorage.getItem('bearerToken');
			client = remoteStorage.createClient(storageInfo, '', token);
		}

		// The client's `get` method takes a key and a callback. The callback will
		// be invoked with an error code and the data.
		client.get(path, function(error, data) {
			if(error==401) {
				alert('Your session has expired. Please connect to your remoteStorage again.');
			} else if(error) {
				alert('Could not find "' + path + '" on the remoteStorage');
				console.log(error);
			} else {
				if (data == undefined) {
					console.log('There wasn\'t anything for "' + path + '"');
				} else {
					console.log('We received this for item "' + path + '": ' + data);
				}
			}

			callback(error, data);
		});
	}

	// For saving data we use the client's `put` method. It takes a key, the
	// value and a callback. The callback will be called with an error code,
	// which is `null` on success.
	function putData(path, value, callback) {
		var storageInfo = JSON.parse(localStorage.getItem('userStorageInfo'));
		var token = localStorage.getItem('bearerToken');
		var client = remoteStorage.createClient(storageInfo, '', token);

		client.put(path, value, function(error) {
			if(error==401) {
				alert('Your session has expired. Please connect to your remoteStorage again.');
			} else if(error) {
				alert('Could not store "' + path + '"');
				console.log(error);
			} else {
				console.log('Stored "' + value + '" for item "' + path + '"');
			}

			callback(error);
		});
	}

	// Now all that's left is to bind the events from the UI elements to
	// these actions, as can be seen [here](app.html).

	return {
		connect: connect,
		authorize: authorize,
		getData: getData,
		putData: putData,
	};

}();
