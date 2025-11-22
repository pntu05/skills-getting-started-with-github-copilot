document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      // Reset activity select options
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Replace the activity card HTML to include a participants section
        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>

          <div class="participants-section">
            <p><strong>Participants</strong></p>
            <ul class="participants-list">
              ${details.participants.length
                ? details.participants.map(p => `<li class="participant-item"><span class="participant-email">${p}</span><button class="delete-btn" title="Unregister" data-email="${p}">&times;</button></li>`).join("")
                : `<li class="muted">No participants yet</li>`}
            </ul>
          </div>
        `;

        // mark activity name for later use by delegated handlers
        activityCard.setAttribute('data-activity', name);
        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Delegate click events for delete buttons (unregister participant)
  activitiesList.addEventListener('click', async (event) => {
    const btn = event.target.closest('.delete-btn');
    if (!btn) return;

    const activityCard = btn.closest('.activity-card');
    if (!activityCard) return;

    const activityName = activityCard.getAttribute('data-activity');
    const email = btn.dataset.email;

    if (!activityName || !email) return;

    if (!confirm(`Unregister ${email} from ${activityName}?`)) return;

    try {
      const resp = await fetch(`/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(email)}`, { method: 'POST' });
      const result = await resp.json();

      if (resp.ok) {
        // Refresh list to reflect changes
        await fetchActivities();
        messageDiv.textContent = result.message;
        messageDiv.className = 'message success';
        messageDiv.classList.remove('hidden');
        setTimeout(() => messageDiv.classList.add('hidden'), 4000);
      } else {
        messageDiv.textContent = result.detail || 'Failed to unregister participant';
        messageDiv.className = 'message error';
        messageDiv.classList.remove('hidden');
      }
    } catch (err) {
      console.error('Error unregistering:', err);
      messageDiv.textContent = 'Failed to unregister. Please try again.';
      messageDiv.className = 'message error';
      messageDiv.classList.remove('hidden');
    }
  });

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "message success";
        signupForm.reset();
        // refresh to show the newly added participant
        await fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "message error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
