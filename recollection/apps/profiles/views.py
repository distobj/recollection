from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from friends.forms import InviteFriendForm
from friends.models import FriendshipInvitation, Friendship

from .models import Profile, nice_username
from .forms import ProfileForm

from avatar.templatetags.avatar_tags import avatar

from Crypto.Cipher import AES
import base64
import hashlib
import urllib
import operator
import array
import simplejson
import time
from datetime import datetime


if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None


def profiles(request, template_name="profiles/profiles.html", extra_context=None):
    if extra_context is None:
        extra_context = {}
    users = User.objects.all().order_by("-date_joined")
    search_terms = request.GET.get('search', '')
    order = request.GET.get('order')
    if not order:
        order = 'date'
    if search_terms:
        users = users.filter(username__icontains=search_terms)
    if order == 'date':
        users = users.order_by("-date_joined")
    elif order == 'name':
        users = users.order_by("username")
    return render_to_response(template_name, dict({
        'users': users,
        'order': order,
        'search_terms': search_terms,
    }, **extra_context), context_instance=RequestContext(request))


def profile(request, username, template_name="profiles/profile.html", extra_context=None):

    if extra_context is None:
        extra_context = {}

    other_user = get_object_or_404(User, username=username)

    if request.user.is_authenticated():
        is_friend = Friendship.objects.are_friends(request.user, other_user)
        other_friends = Friendship.objects.friends_for_user(other_user)
        if request.user == other_user:
            is_me = True
        else:
            is_me = False
        previous_invitations_to = FriendshipInvitation.objects.invitations(to_user=other_user, from_user=request.user)
        previous_invitations_from = FriendshipInvitation.objects.invitations(to_user=request.user, from_user=other_user)
    else:
        other_friends = []
        is_friend = False
        is_me = False

        previous_invitations_to = None
        previous_invitations_from = None

    if is_friend:
        invite_form = None
        if request.method == "POST":
            if request.POST.get("action") == "remove": # @@@ perhaps the form should just post to friends and be redirected here
                Friendship.objects.remove(request.user, other_user)
                request.user.message_set.create(message=_("You have removed %(from_user)s from friends") % {'from_user': other_user})
                is_friend = False
                invite_form = InviteFriendForm(request.user, {
                    'to_user': username,
                    'message': ugettext("Let's Connect!"),
                })

    else:
        if request.user.is_authenticated() and request.method == "POST":
            if request.POST.get("action") == "invite": # @@@ perhaps the form should just post to friends and be redirected here
                invite_form = InviteFriendForm(request.user, request.POST)
                if invite_form.is_valid():
                    invite_form.save()
            else:
                invite_form = InviteFriendForm(request.user, {
                    'to_user': username,
                    'message': ugettext("Let's be friends!"),
                })
                invitation_id = request.POST.get("invitation", None)
                if request.POST.get("action") == "accept": # @@@ perhaps the form should just post to friends and be redirected here
                    try:
                        invitation = FriendshipInvitation.objects.get(id=invitation_id)
                        if invitation.to_user == request.user:
                            invitation.accept()
                            request.user.message_set.create(message=_("You have accepted the connection request from %(from_user)s") % {'from_user': invitation.from_user})
                            is_friend = True
                            other_friends = Friendship.objects.friends_for_user(other_user)
                    except FriendshipInvitation.DoesNotExist:
                        pass
                elif request.POST.get("action") == "decline": # @@@ perhaps the form should just post to friends and be redirected here
                    try:
                        invitation = FriendshipInvitation.objects.get(id=invitation_id)
                        if invitation.to_user == request.user:
                            invitation.decline()
                            request.user.message_set.create(message=_("You have declined the connection request from %(from_user)s") % {'from_user': invitation.from_user})
                            other_friends = Friendship.objects.friends_for_user(other_user)
                    except FriendshipInvitation.DoesNotExist:
                        pass
        else:
            invite_form = InviteFriendForm(request.user, {
                'to_user': username,
                'message': ugettext("Let's Connect!"),
            })

    return render_to_response(template_name, dict({
        "is_me": is_me,
        "is_friend": is_friend,
        "other_user": other_user,
        "other_friends": other_friends,
        "invite_form": invite_form,
        "previous_invitations_to": previous_invitations_to,
        "previous_invitations_from": previous_invitations_from,
    }, **extra_context), context_instance=RequestContext(request))


@login_required
def profile_edit(request, form_class=ProfileForm, **kwargs):

    template_name = kwargs.get("template_name", "profiles/profile_edit.html")

    if request.is_ajax():
        template_name = kwargs.get(
            "template_name_facebox",
            "profiles/profile_edit_facebox.html"
        )

    profile = request.user.get_profile()

    if request.method == "POST":
        profile_form = form_class(request.POST, instance=profile)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = request.user
            profile.save()
            return HttpResponseRedirect(reverse("profile_detail", args=[request.user.username]))
    else:
        profile_form = form_class(instance=profile)

    return render_to_response(template_name, {
        "profile": profile,
        "profile_form": profile_form,
    }, context_instance=RequestContext(request))

@login_required
def uservoice_token(request, **kwargs):
    """
    Return a UserVoice single-sign-on (SSO) token

    Code derived from http://developer.uservoice.com/docs/single-sign-on-how-to
    """

    # Calc expiry time. UV needs it in GMT
    dt=time.mktime(request.session.get_expiry_date().timetuple())
    utc_dt = datetime.fromtimestamp(dt)
    expires = utc_dt.strftime("%Y-%m-%d %H:%M:%S")

    sso_data = {
        'guid': request.user.username,
        'expires': expires,
        'email': request.user.email,
        'display_name': nice_username(request.user),
        'admin': 'accept' if request.user.is_staff else 'deny',
    }

    block_size = 16
    mode = AES.MODE_CBC

    invalid_key = 'invalid-key'
    if 'USERVOICE_SETTINGS' in dir(settings):
        api_key = settings.USERVOICE_SETTINGS.get('API_KEY',invalid_key)
        account_key = settings.USERVOICE_SETTINGS.get('ACCOUNT_KEY',invalid_key)
    else:
        # Disable SSO by using a garbage key. Will result in logged auth
        # failures in the Uservoice admin console.
        api_key = invalid_key
        account_key = invalid_key

    iv = "OpenSSL for Ruby"

    json = simplejson.dumps(sso_data, separators=(',',':'))

    salted = api_key+account_key
    saltedHash = hashlib.sha1(salted).digest()[:16]

    json_bytes = array.array('b', json[0 : len(json)])
    iv_bytes = array.array('b', iv[0 : len(iv)])

    # # xor the iv into the first 16 bytes.
    for i in range(0, 16):
        json_bytes[i] = operator.xor(json_bytes[i], iv_bytes[i])

    pad = block_size - len(json_bytes.tostring()) % block_size
    data = json_bytes.tostring() + pad * chr(pad)
    aes = AES.new(saltedHash, mode, iv)
    encrypted_bytes = aes.encrypt(data)

    param_for_uservoice_sso = urllib.quote(base64.b64encode(encrypted_bytes))

    return HttpResponse(param_for_uservoice_sso,mimetype='text/plain')
