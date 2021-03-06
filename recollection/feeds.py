from django.contrib.syndication.feeds import Feed
from django.utils.feedgenerator import Atom1Feed
from freemix.utils import get_user
from freemix.dataprofile.models import DataProfile
from freemix.freemixprofile.models import Freemix
from freemix.utils import get_site_url
from django.conf import settings
from django.http import Http404

from django.core.urlresolvers import reverse

# TODO: English strings!  Need I18N in feeds?

class LatestDataViews(Feed):
    title = "Latest Data Views"
    description = "Latest Data Views"
    link = get_site_url()

    def items(self):
        return Freemix.objects.order_by('-created')[:10]


class AtomLatestDataViews(LatestDataViews):
    feed_type = Atom1Feed
    subtitle = LatestDataViews.description


class UserDataViews(Feed):

    # Parse the username from the URL
    def get_object(self, urltail):
        if len(urltail) != 1:
            raise Http404
        return get_user(username=urltail[0])

    def title(self, obj):
        return "Latest Data Views created by %(user)s" % { 'user': obj.username }

    def description(self, obj):
        return "Latest Data Views for %(user)s" % { 'user': obj.username }

    # Link to user's profile
    def link(self, obj):
        return get_site_url(reverse("profile_detail", kwargs={'username':
                    obj.username}))
    # Return only this user's Freemixes.
    def items(self, obj):
        return Freemix.objects.filter(user=obj).order_by('-created')[:10]


class AtomUserDataViews(UserDataViews):
    feed_type = Atom1Feed
    subtitle = UserDataViews.description

class LatestDatasets(Feed):
    title = "Datasets"
    description = "Latest Datasets"

    link = get_site_url()

    def items(self):
        return DataProfile.objects.order_by('-created')[:10]


class AtomLatestDatasets(LatestDatasets):
    feed_type = Atom1Feed
    subtitle = LatestDatasets.description


class UserDatasets(Feed):

    # Parse the username from the URL
    def get_object(self, urltail):
        if len(urltail) != 1:
            raise Http404
        return get_user(username=urltail[0])

    def title(self, obj):
        return "Latest Datasets created by %s" % obj.username

    def description(self, obj):
        return "Latest Datasets for %(user)s" % { 'user': obj.username }

    # Link to user's profile
    def link(self, obj):
        return get_site_url(reverse("profile_detail", kwargs={'username':
                    obj.username}))

    # Return only this user's data.
    def items(self, obj):
        return DataProfile.objects.filter(user=obj).order_by('-created')[:10]


class AtomUserDatasets(UserDatasets):
    feed_type = Atom1Feed
    subtitle = UserDatasets.description

