<script>
  import { onMount } from 'svelte';
  import * as api from '../lib/api.js';
  import { currentUser, showToast } from '../lib/stores.js';

  let name = '';
  let email = '';
  let phone = '';
  let emergencyContact = '';
  let role = '';

  onMount(async () => {
    // Populate form from currently logged in user state
    const user = $currentUser;
    if (user) {
      name = user.name;
      email = user.email;
      phone = user.phone || '';
      role = user.role;
      
      if (user.role === 'tenant') {
        try {
          const tenants = await api.getTenants();
          const t = tenants.find(x => x.user_id === user.id);
          if (t) {
            emergencyContact = t.emergency_contact || '';
          }
        } catch (e) {
          console.error(e);
        }
      }
    }
  });

  async function handleProfileSubmit(e) {
    e.preventDefault();
    try {
      const updatedUser = await api.updateUserProfile($currentUser.id, {
        name,
        email,
        phone,
        emergency_contact: role === 'tenant' ? emergencyContact : null
      });
      currentUser.set(updatedUser);
      showToast('Profile settings updated successfully!', 'success');
    } catch (err) {
      showToast(err.message, 'error');
    }
  }
</script>

<div class="view-section active" style="display: flex; flex-direction: column; gap: 24px;">
  <div class="card" style="max-width: 500px; margin: 0;">
    <div class="section-header" style="margin-bottom: 20px;">
      <div class="section-title">Edit My Profile Settings</div>
    </div>
    
    <form on:submit={handleProfileSubmit}>
      <div class="form-group">
        <label class="form-label" for="profileName">Full Name</label>
        <input type="text" id="profileName" bind:value={name} class="form-control" required>
      </div>

      <div class="form-group">
        <label class="form-label" for="profileEmail">Email Address</label>
        <input type="email" id="profileEmail" bind:value={email} class="form-control" required>
      </div>

      <div class="form-group">
        <label class="form-label" for="profilePhone">Phone Number</label>
        <input type="text" id="profilePhone" bind:value={phone} class="form-control" required>
      </div>

      {#if role === 'tenant'}
        <div class="form-group">
          <label class="form-label" for="profileEmergency">Emergency Contact Details</label>
          <input type="text" id="profileEmergency" bind:value={emergencyContact} class="form-control" placeholder="e.g. Amit Sharma: +91 98765 99991">
        </div>
      {/if}

      <div style="margin-top: 20px; display: flex; justify-content: flex-end;">
        <button type="submit" class="topbar-btn primary"><i class="ti ti-device-floppy"></i> Save Changes</button>
      </div>
    </form>
  </div>
</div>
