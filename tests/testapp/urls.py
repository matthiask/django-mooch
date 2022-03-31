from django.contrib import admin
from django.urls import include, path
from testapp.models import Payment

from mooch.banktransfer import BankTransferMoocher
from mooch.postfinance import PostFinanceMoocher


admin.autodiscover()


banktransfer_moocher = BankTransferMoocher(model=Payment, autocharge=True)
postfinance_moocher = PostFinanceMoocher(
    model=Payment, pspid="test", live=False, sha1_in="nothing", sha1_out="nothing"
)

moochers = [
    path("", include(banktransfer_moocher.urls)),
    path("", include(postfinance_moocher.urls)),
]

urlpatterns = [path("admin/", admin.site.urls), path("", include((moochers, "mooch")))]
