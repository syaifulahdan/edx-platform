""" Journal Tab of Learner Dashboard views """
from datetime import datetime, time
from django.conf import settings
from django.http import Http404
from urlparse import urljoin

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
        journal['url'] = get_journal_about_page_url(slug=journal['journal']['journalaboutpage']['slug'])
        journal['expiration_date'] = str(journal['expiration_date'])
        journal['overview'] = JournalOverview(journal)

    context = {
        'journals': journals,
    }

    return render_to_response('journal_dashboard.html', context)



def get_journal_about_page_url(slug=''):
    """
    Returns the url of a journal about page for the given journal slug.
    """
    return urljoin(settings.JOURNALS_ROOT_URL, slug)


class JournalOverview(object):
    """ Contains all data needed to generate a Journal Card"""

    def __init__(self, journal):
        """
        Arguments:
              journal (dict): journal dict containing info from the journal access api
        """
        # set expiration date to be the last second of the day it expires
        self.expiration_datetime = datetime.combine(
            date=datetime.strptime(journal['expiration_date'], '%Y-%m-%d').date(),
            time=time.max
        )
        self.expiration_date_formatted = self.expiration_datetime.strftime("%b %d %Y")




