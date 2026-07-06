from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from recruiter_app.views import (
    recruiter_signup, recruiter_login, recruiter_dashboard, recruiter_profile,
    recruiter_logout, homepage, recruiter_profile_update, job_details,
    applied_job, approve, my_jobs, delete_job
)
from candidate_app.views import (
    candidate_dashboard, candidate_login, candidate_logout, candidate_profile,
    candidate_signup, candidate_profile_update, view_detail, apply_job, scheduled
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", homepage, name="homepage"),

    # Recruiter URLs
    path("r_signup/", recruiter_signup, name="recruiter_signup"),
    path("r_login/", recruiter_login, name="recruiter_login"),
    path("r_dashboard/", recruiter_dashboard, name="recruiter_dashboard"),
    path("r_profile/", recruiter_profile, name="recruiter_profile"),
    path("r_logout/", recruiter_logout, name="recruiter_logout"),
    path("r_profile_update/", recruiter_profile_update, name="recruiter_profile_update"),
    path("job_details/", job_details, name="job_details"),
    path("my_jobs/", my_jobs, name="my_jobs"),
    path("delete_job/<int:id>", delete_job, name="delete_job"),
    path("applied_job/", applied_job, name="applied_job"),
    path("approve/<int:id>", approve, name="approve"),

    # Candidate URLs
    path("c_signup/", candidate_signup, name="candidate_signup"),
    path("c_login/", candidate_login, name="candidate_login"),
    path("c_dashboard/", candidate_dashboard, name="candidate_dashboard"),
    path("c_profile/", candidate_profile, name="candidate_profile"),
    path("c_logout/", candidate_logout, name="candidate_logout"),
    path('c_profile_update/', candidate_profile_update, name="candidate_profile_update"),
    path("view_detail/<int:id>", view_detail, name="view_detail"),
    path("apply_job/<int:id>", apply_job, name="apply_job"),
    path("result/", scheduled, name="result"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
