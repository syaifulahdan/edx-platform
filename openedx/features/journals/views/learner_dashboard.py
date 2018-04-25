""" Journal Tab of Learner Dashboard views """
from datetime import datetime, time
from django.conf import settings
from django.http import Http404
from urlparse import urljoin, urlsplit, urlunsplit

from edxmako.shortcuts import render_to_response
from openedx.features.journals.api import JournalsApiClient, journals_enabled

import logging
logger = logging.getLogger(__name__)

def journal_listing(request):
    """ View a list of journals which the user has or had access to"""
    #TODO: check assumption, list journals that user HAD access to but no longer does

    # import pdb; pdb.set_trace()
    user = request.user

    if not journals_enabled() or not user.is_authenticated():
        raise Http404

    journal_client = JournalsApiClient()
    journals = journal_client.get_journal_access(user)

    #TODO: convert all this to the journal overview object
    #TODO: pass list of journal overview objects back instead of the journal dicts

    for journal in journals:
        journal['expiration_date'] = str(journal['expiration_date'])
        journal['overview'] = JournalOverview(journal)

    context = {
        'journals': journals,
    }

    return render_to_response('journal_dashboard.html', context)


class JournalOverview(object):
    """ Contains all data needed to generate a Journal Card"""

    def __init__(self, journal):
        """
        Arguments:
              journal (dict): journal dict containing info from the journal access api
        """
        self.journal = journal

        # set expiration date to be the last second of the day it expires
        self.expiration_datetime = datetime.combine(
            date=datetime.strptime(journal['expiration_date'], '%Y-%m-%d').date(),
            time=time.max
        )
        self.expiration_date_formatted = self.expiration_datetime.strftime("%b %d %Y")

        self.title = journal['journal']['name']

        self.about_page_url = self.get_journal_about_page_url()

    def get_journal_about_page_url(self):
        """
        Return url to journal about page.
        The url will redirect through the journals service log in page.  Otherwise the user may be
        sent to a page to purchase the book - and that is an awkward user experience.
        """
        login_url = urljoin(settings.JOURNALS_ROOT_URL, 'login')

        slug = self.journal['journal']['journalaboutpage']['slug']
        about_page_url = urljoin(settings.JOURNALS_ROOT_URL, slug)
        query = 'next={next_url}'.format(next_url=about_page_url)

        split_url = urlsplit(login_url)
        url = urlunsplit((
            split_url.scheme,
            split_url.netloc,
            split_url.path,
            query,
            split_url.fragment,
        ))
        return url
