
function validateForm() {
    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const age = document.getElementById("age").value;
    const gender = document.getElementById("gender").value;
    const course = document.getElementById("course").value;
    const password = document.getElementById("password").value;

    if (!name || !email || !age || !gender || !course || !password) {
        alert("Please fill in all fields.");
        return false;
    }

    if (!/^\d+$/.test(age) || Number(age) < 1) {
        alert("Please enter a valid numeric age.");
        return false;
    }

    if (password.length < 6) {
        alert("Password must contain at least 6 characters.");
        return false;
    }

    alert("Validation successful!");
    return true;
}


// Level 4: Profile page interactions
$(document).ready(function () {

    // Live time, updated every second
    if ($("#clock").length) {
        function updateClock() {
            $("#clock").text(new Date().toLocaleTimeString());
        }

        updateClock();
        setInterval(updateClock, 1000);
    }

    // Show or hide student details
    $("#toggleBtn").click(function () {
        $("#details").toggle();
    });

    // Update course using jQuery AJAX
    $("#newCourse").change(function () {
        const selectedCourse = $(this).val();

        $.post("/update-course", {
            course: selectedCourse
        })
        .done(function (response) {
            $("#currentCourse").text(response.course);
            $("#message").text(response.message).css("color", "green");
        })
        .fail(function (xhr) {
            const error = xhr.responseJSON?.error || "Course update failed.";
            $("#message").text(error).css("color", "red");
        });
    });
});
