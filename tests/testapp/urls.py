from django.conf.urls import include, url
from django.contrib import admin

from mooch.banktransfer import BankTransferMoocher
from mooch.postfinance import PostFinanceMoocher
from testapp.models import Payment


admin.autodiscover()


banktransfer_moocher = BankTransferMoocher(model=Payment, autocharge=True)
postfinance_moocher = PostFinanceMoocher(
    model=Payment, pspid="test", live=False, sha1_in="nothing", sha1_out="nothing"
)

moochers = [
    url(r"", include(banktransfer_moocher.urls)),
    url(r"", include(postfinance_moocher.urls)),
]

urlpatterns = [url(r"^admin/", admin.site.urls), url(r"", include((moochers, "mooch")))]
