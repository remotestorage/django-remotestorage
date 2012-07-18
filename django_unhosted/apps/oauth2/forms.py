#-*- coding: utf-8 -*-

import itertools as it, operator as op, functools as ft

from django import forms

from crispy_forms.helpers import FormHelper, Submit, Hidden, Reset


class AuthorizeForm(forms.Form):

	authorize = forms.ChoiceField(
		widget=forms.HiddenInput, choices=[('Yes', 'Yes'), ('No', 'No')] )

	_cap_desc = dict(r='read', w='write')

	def __init__(self, *argz, **kwz):
		paths, app, action = it.imap(kwz.pop, ['paths', 'app', 'action'])

		access_choices = list()
		for path in paths:
			try: path, caps = path.rsplit(':', 1)
			except ValueError: caps = 'rw'
			assert ':' not in path
			access_choices.extend(
				('{}:{}'.format(path, cap), '{}: {}'.format(cap_desc, path))
				for cap, cap_desc in list((k, self._cap_desc[k]) for k in caps) )

		self.helper = fh = FormHelper()
		fh.add_input(Submit('authorize', 'No'))
		fh.add_input(Submit('authorize', 'Yes'))
		fh.form_action, fh.form_method = action, 'POST'

		super(AuthorizeForm, self).__init__(*argz, **kwz)

		self.fields['path_access'] = forms.MultipleChoiceField(
			label='Grant “{}” access to the following storage paths:'.format(app),
			widget=forms.CheckboxSelectMultiple, required=False,
			choices=access_choices, initial=map(op.itemgetter(0), access_choices) )
