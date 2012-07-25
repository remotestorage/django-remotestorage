$(function() {

	$('#connect').on('click', function() {
		var userAddress = $('#userAddress').val();

		helper.showSpinner('connectionSpinner');

		storage.connect(userAddress, function(error, storageInfo) {
			if(error) {
				helper.setConnectionState(false);
			} else {
				localStorage.setItem('userStorageInfo', JSON.stringify(storageInfo));
				localStorage.setItem('userAddress', userAddress);
				helper.setConnectionState(true);
			}

			helper.hideSpinner('connectionSpinner');
		});

		return false;
	});

	$('#fetchPublicKey').on('click', function() {
		var key = $('#publicKey').val();

		helper.showSpinner('fetchPublicSpinner');

		storage.getData('public/tutorial/'+key, function(error, data) {
			if(!error && data != "null") {
				$('#publicValue').val(data);
			}

			helper.hideSpinner('fetchPublicSpinner');
		});

		return false;
	});

	$('#publishPublic').on('click', function() {
		var key = $('#publicKey').val();
		var value = $('#publicValue').val();

		helper.showSpinner('publishPublicSpinner');

		storage.putData('public/tutorial/'+key, value, function(error) {
			if (!error) {
				$('#publicValue').val('');
			}

			helper.hideSpinner('publishPublicSpinner');
		});

		return false;
	});

	$('#authorize').on('click', function() {
		storage.authorize(['public/tutorial:rw', 'tutorial:rw']);
		return false;
	});

	$('#publishTutorial').on('click', function() {
		var key = $('#tutorialKey').val();
		var value = $('#tutorialValue').val();

		helper.showSpinner('publishTutorialSpinner');

		storage.putData('tutorial/'+key, value, function(error) {
			if (!error) {
				$('#tutorialValue').val('');
			}

			helper.hideSpinner('publishTutorialSpinner');
		});

		return false;
	});

	$('#fetchTutorialKey').on('click', function() {
		var key = $('#tutorialKey').val();

		helper.showSpinner('fetchTutorialSpinner');

		storage.getData('tutorial/'+key, function(error, data) {
			if(!error && data !== "null") {
				$('#tutorialValue').val(data);
			}

			helper.hideSpinner('fetchTutorialSpinner');
		});

		return false;
	});

	$('#disconnect').on('click', function() {
		helper.disconnect();
		return false;
	});

	$('#deauthorize').on('click', function() {
		helper.deauthorize();
		return false;
	});

	helper.setConnectionState(helper.isConnected());
	helper.setAuthorizedState(helper.isAuthorized());
});
