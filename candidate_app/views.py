from django.shortcuts import render, redirect
from django.http import HttpResponse
from candidate_app.models import Candidate, CandidateDetail
from recruiter_app.models import JobDetail, Recruiter, JobApplied
from django.views.decorators.cache import never_cache
import smtplib
from email.mime.text import MIMEText


def candidate_signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        name = request.POST.get("fullname")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")

        # Check if username already exists
        if Candidate.objects.filter(username=username).exists():
            return render(request, "./candidate_app/signup.html", {"error": "Username already taken."})

        Candidate.objects.create(
            username=username,
            name=name,
            email=email,
            phone=phone,
            password=password
        )
        return redirect("candidate_login")
    else:
        return render(request, "./candidate_app/signup.html")


@never_cache
def candidate_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = Candidate.objects.filter(username=username, password=password).first()

        if user:
            request.session["candidate_id"] = user.id
            request.session["candidate_username"] = user.username
            request.session["candidate_name"] = user.name
            request.session["candidate_email"] = user.email
            request.session["candidate_phone"] = user.phone

            # Email notification
            sender = "jayanthagatti2003@gmail.com"
            receiver = user.email
            gmail_password = "gxbl ynwt mwjn ijvb"
            message = "Login successful"
            subject = "Login Notification"
            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = receiver
            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(sender, gmail_password)
                server.send_message(msg)
                server.quit()
            except Exception as e:
                print(e)

            return redirect("candidate_dashboard")
        else:
            return render(request, "./candidate_app/login.html", {"error": "Invalid username or password."})
    else:
        return render(request, "./candidate_app/login.html")


@never_cache
def candidate_dashboard(request):
    if "candidate_username" not in request.session:
        return redirect("candidate_login")

    username = request.session.get("candidate_name")
    search_query = request.GET.get("search", "").strip()

    jobs = JobDetail.objects.all()

    if search_query:
        jobs = jobs.filter(
            job_role__icontains=search_query
        ) | jobs.filter(
            company_name__icontains=search_query
        ) | jobs.filter(
            job_location__icontains=search_query
        ) | jobs.filter(
            skills_required__icontains=search_query
        )

    # Get IDs of jobs already applied by this candidate
    candidate_id = request.session.get("candidate_id")
    applied_job_ids = set(
        JobApplied.objects.filter(candidate_id=candidate_id).values_list("job_detail_id", flat=True)
    )

    return render(request, "./candidate_app/dashboard.html", {
        "username": username,
        "a": jobs,
        "search_query": search_query,
        "applied_job_ids": applied_job_ids,
    })


@never_cache
def candidate_profile(request):
    if "candidate_username" not in request.session:
        return redirect("candidate_login")

    userid = request.session.get("candidate_id")
    name = request.session.get("candidate_name")
    email = request.session.get("candidate_email")
    phone = request.session.get("candidate_phone")

    user = CandidateDetail.objects.filter(user_id=userid).first()

    if user:
        bio = user.bio
        address = user.address
        city = user.city
        state = user.state
        profile_pic = user.profile_pic
        resume = user.resume
    else:
        bio = address = city = state = None
        profile_pic = resume = None

    context = {
        "name": name,
        "email": email,
        "phone": phone,
        "bio": bio,
        "address": address,
        "city": city,
        "state": state,
        "profile_pic": profile_pic,
        "resume": resume,
    }
    return render(request, "./candidate_app/profile.html", context)


@never_cache
def candidate_profile_update(request):
    if "candidate_username" not in request.session:
        return redirect("candidate_login")

    candidate_id = request.session.get("candidate_id")
    candidate = Candidate.objects.get(id=candidate_id)
    existing = CandidateDetail.objects.filter(user=candidate).first()

    if request.method == "POST":
        bio = request.POST.get("bio")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        pincode = request.POST.get("pincode", "")
        country = request.POST.get("country", "")
        image = request.FILES.get("image")
        resume = request.FILES.get("resume")

        defaults = {
            "bio": bio,
            "address": address,
            "city": city,
            "state": state,
            "pincode": pincode,
            "country": country,
        }
        if image:
            defaults["profile_pic"] = image
        if resume:
            defaults["resume"] = resume

        CandidateDetail.objects.update_or_create(
            user=candidate,
            defaults=defaults
        )
        return redirect("candidate_profile")

    return render(request, "./candidate_app/profile_update.html", {"existing": existing})


from recruiter_app.models import RecruiterDetail


@never_cache
def view_detail(request, id):
    if "candidate_username" not in request.session:
        return redirect("candidate_login")

    job = JobDetail.objects.select_related('recruiter').filter(id=id).first()
    recruiter_detail = RecruiterDetail.objects.filter(user=job.recruiter).first()

    # Check if already applied
    candidate_id = request.session.get("candidate_id")
    already_applied = JobApplied.objects.filter(candidate_id=candidate_id, job_detail=job).exists()

    context = {
        "job": job,
        "recruiter": job.recruiter,
        "recruiter_detail": recruiter_detail,
        "already_applied": already_applied,
    }
    return render(request, "./candidate_app/view_detail.html", context)


@never_cache
def apply_job(request, id):
    if "candidate_username" not in request.session:
        return redirect("candidate_login")

    candidate_id = request.session.get("candidate_id")
    candidate = Candidate.objects.filter(id=candidate_id).first()
    job = JobDetail.objects.filter(id=id).first()

    # Prevent duplicate applications
    already_applied = JobApplied.objects.filter(candidate=candidate, job_detail=job).exists()
    if already_applied:
        return redirect("candidate_dashboard")

    recruiter = job.recruiter
    JobApplied.objects.create(
        job_detail=job,
        recruiter=recruiter,
        candidate=candidate,
        scheduled=False
    )
    return redirect("result")


def scheduled(request):
    if "candidate_username" not in request.session:
        return redirect("candidate_login")
    userid = request.session.get("candidate_id")
    applications = JobApplied.objects.filter(candidate=userid).select_related("job_detail", "job_detail__recruiter")
    return render(request, "./candidate_app/result.html", {"user": applications})


@never_cache
def candidate_logout(request):
    request.session.flush()
    return redirect("candidate_login")
