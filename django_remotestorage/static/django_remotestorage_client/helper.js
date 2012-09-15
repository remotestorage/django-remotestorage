helper = function() {

	var connected = false;
	var authorized = false;

	function setConnectionState(state) {
		connected = state;

		elementIds = [
			'publicKey', 'fetchPublicKey', 'authorize', 'disconnect'
		];

		if (connected) {
			for (var i = 0; i < elementIds.length; i++) {
				$('#' + elementIds[i]).removeAttr('disabled');
			}
			$('#connectionState').html('connected');
			$('#connect').hide();
			$('#disconnect').show();
			$('#userAddress').val(localStorage.getItem('userAddress'));
		} else {
			for (var i = 0; i < elementIds.length; i++) {
				$('#' + elementIds[i]).attr('disabled', 'disabled');
			}
			$('#connectionState').html('disconnected');
			$('#connect').show();
			$('#disconnect').hide();
			$('#userAddress').val('');
			deauthorize();
		}
		$('#connectionState').toggleClass('enabled', connected);

		$('#states').show();
	}

	function isConnected() {
		return localStorage.getItem('userStorageInfo') != null;
	}

	function disconnect() {
		localStorage.removeItem('userStorageInfo');
		localStorage.removeItem('userAddress');
		setConnectionState(false);
	}

	function setAuthorizedState(state) {
		authorized = state;

		elementIds = [
			'tutorialKey', 'fetchTutorialKey', 'tutorialValue',
			'publishTutorial', 'publicValue', 'publishPublic', 'deauthorize'
		];

		if (authorized) {
			for (var i = 0; i < elementIds.length; i++) {
				$('#' + elementIds[i]).removeAttr('disabled');
			}
			$('#publicTitle').html('Read/write access for "public" category');
			$('#authorizedState').html('authorized');
			$('#authorize').hide();
			$('#deauthorize').show();
		} else {
			for (var i = 0; i < elementIds.length; i++) {
				$('#' + elementIds[i]).attr('disabled', 'disabled');
			}
			$('#publicTitle').html('Read access for "public" category');
			$('#authorizedState').html('not authorized');
			$('#authorize').show();
			$('#deauthorize').hide();
		}
		$('#authorizedState').toggleClass('enabled', authorized);
	}

	function isAuthorized() {
		return localStorage.getItem('bearerToken') != null;
	}

	function deauthorize() {
		localStorage.removeItem('bearerToken');
		setAuthorizedState(false);
	}


	function showSpinner(id) {
		$('#' + id).show();
	}

	function hideSpinner(id) {
		$('#' + id).hide();
	}

	return {
		setConnectionState: setConnectionState,
		isConnected: isConnected,
		disconnect: disconnect,
		setAuthorizedState: setAuthorizedState,
		isAuthorized: isAuthorized,
		deauthorize: deauthorize,
		showSpinner: showSpinner,
		hideSpinner: hideSpinner
	};

}();
