/*
Copyright 2012 Unhosted

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

*/
var helper = (function() {
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
    isConnected:        isConnected,
    disconnect:         disconnect,
    setAuthorizedState: setAuthorizedState,
    isAuthorized:       isAuthorized,
    deauthorize:        deauthorize,
    showSpinner:        showSpinner,
    hideSpinner:        hideSpinner
  };
})();
