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
(function(storage, helper) {

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

})(tutorial, helper);
