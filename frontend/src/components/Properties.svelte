<script>
  import { onMount } from 'svelte';
  import * as api from '../lib/api.js';
  import { globalSearch, showToast } from '../lib/stores.js';
  import { formatCurrency } from '../lib/utils.js';

  export let user = null;
  export let activePropertyId = null;

  let properties = [];
  let loading = true;
  let selectedProperty = null;
  let reviews = [];
  let ratingValue = 5;
  let reviewComment = '';

  // Filter criteria
  let typeFilter = 'all';
  let statusFilter = 'all';

  // Reactively open details if activePropertyId changes or is set
  $: if (activePropertyId && properties.length > 0) {
    const p = properties.find(x => String(x.id) === String(activePropertyId));
    if (p) {
      openDetails(p);
      activePropertyId = null; // reset prop
    }
  }

  // Details Modal variables
  let activeDetailsIdx = 0;
  let showDetailsModal = false;

  // Add/Edit Modal variables
  let showPropertyModal = false;
  let editMode = false;
  let propId = '';
  let propTitle = '';
  let propAddress = '';
  let propCity = '';
  let propState = '';
  let propPincode = '';
  let propImageUrl = '';
  let propType = 'flat';
  let propRent = '';
  let propBedrooms = '';
  let propBathrooms = '';
  let propStatus = 'vacant';
  let propDesc = '';
  let propOwnerName = '';
  let propOwnerEmail = '';
  let propOwnerPhone = '';
  let propInteriorImages = '';

  onMount(async () => {
    await loadProperties();
  });

  async function loadProperties() {
    try {
      loading = true;
      properties = await api.getProperties();
    } catch (e) {
      showToast('Error loading properties: ' + e.message, 'error');
    } finally {
      loading = false;
    }
  }

  // Details Modal open
  async function openDetails(p) {
    selectedProperty = p;
    activeDetailsIdx = 0;
    showDetailsModal = true;
    try {
      reviews = await api.getPropertyReviews(p.id);
    } catch (err) {
      console.error(err);
      reviews = [];
    }
  }

  function closeDetails() {
    showDetailsModal = false;
    selectedProperty = null;
    reviews = [];
    ratingValue = 5;
    reviewComment = '';
  }

  // Create Review
  async function handleSubmitReview() {
    if (!reviewComment.trim()) return;
    try {
      const newReview = await api.createPropertyReview(selectedProperty.id, {
        rating: ratingValue,
        comment: reviewComment
      });
      reviews = [newReview, ...reviews];
      showToast('Review submitted successfully!', 'success');
      reviewComment = '';
      ratingValue = 5;
    } catch (e) {
      showToast(e.message, 'error');
    }
  }

  // Book property action
  async function handleBookNow(p) {
    if (!user) {
      showToast('Please sign in to request booking', 'warning');
      return;
    }
    // Get tenant profile
    try {
      const tenants = await api.getTenants();
      const tenant = tenants.find(t => t.user_id === user.id);
      if (!tenant) {
        showToast('Tenant profile not found. Please onboard first.', 'error');
        return;
      }
      
      const startDate = new Date().toISOString().slice(0, 10);
      const endDate = new Date();
      endDate.setFullYear(endDate.getFullYear() + 1);
      const endDateStr = endDate.toISOString().slice(0, 10);

      await api.createBookingRequest({
        property_id: p.id,
        tenant_id: tenant.id,
        start_date: startDate,
        end_date: endDateStr
      });
      
      showToast('Booking request submitted successfully! Manager will review it.', 'success');
      closeDetails();
      await loadProperties();
    } catch (e) {
      showToast(e.message, 'error');
    }
  }

  // Edit Modal open
  function openAddModal() {
    editMode = false;
    propId = '';
    propTitle = '';
    propAddress = '';
    propCity = '';
    propState = '';
    propPincode = '';
    propImageUrl = '';
    propType = 'flat';
    propRent = '';
    propBedrooms = '';
    propBathrooms = '';
    propStatus = 'vacant';
    propDesc = '';
    propOwnerName = '';
    propOwnerEmail = '';
    propOwnerPhone = '';
    propInteriorImages = '';
    showPropertyModal = true;
  }

  function openEditModal(p, event) {
    if (event) event.stopPropagation();
    editMode = true;
    propId = p.id;
    propTitle = p.title;
    propAddress = p.address;
    propCity = p.city || '';
    propState = p.state || '';
    propPincode = p.pincode || '';
    propImageUrl = p.image_url || '';
    propType = p.type || 'flat';
    propRent = p.rent_amount;
    propBedrooms = p.bedrooms || '';
    propBathrooms = p.bathrooms || '';
    propStatus = p.status;
    propDesc = p.description || '';
    propOwnerName = p.owner_name || '';
    propOwnerEmail = p.owner_email || '';
    propOwnerPhone = p.owner_phone || '';
    propInteriorImages = p.interior_images || '';
    showPropertyModal = true;
  }

  async function handlePropertySubmit(e) {
    e.preventDefault();
    const payload = {
      title: propTitle,
      address: propAddress,
      city: propCity,
      state: propState,
      pincode: propPincode,
      image_url: propImageUrl || 'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=800&q=80',
      type: propType,
      rent_amount: parseInt(propRent),
      bedrooms: propBedrooms ? parseInt(propBedrooms) : null,
      bathrooms: propBathrooms ? parseInt(propBathrooms) : null,
      status: propStatus,
      description: propDesc,
      owner_name: propOwnerName,
      owner_email: propOwnerEmail,
      owner_phone: propOwnerPhone,
      interior_images: propInteriorImages
    };

    try {
      if (editMode) {
        await api.updateProperty(propId, payload);
        showToast('Property updated successfully', 'success');
      } else {
        await api.createProperty(payload);
        showToast('Property registered successfully', 'success');
      }
      showPropertyModal = false;
      await loadProperties();
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  async function handleDeleteProperty(p, event) {
    if (event) event.stopPropagation();
    if (confirm(`Are you sure you want to delete "${p.title}" permanently? All associated bookings, maintenance, reviews, and lease agreements will be deleted!`)) {
      try {
        await api.deleteProperty(p.id);
        showToast('Property and all associated features deleted successfully.', 'success');
        await loadProperties();
      } catch (err) {
        showToast(err.message, 'error');
      }
    }
  }

  $: getCardImages = (p) => {
    if (!p) return [];
    const list = [p.image_url];
    if (p.interior_images) {
      p.interior_images.split(',').forEach(url => {
        if (url.trim()) list.push(url.trim());
      });
    }
    return list.slice(0, 4); // show up to 4 thumbnails on card scroll
  };

  $: {
    if (selectedProperty) {
      console.log("selectedProperty is: ", selectedProperty);
      console.log("getCardImages(selectedProperty):", getCardImages(selectedProperty));
    }
  }

  $: filteredProperties = properties.filter(p => {
    const searchStr = $globalSearch.toLowerCase();
    const matchesSearch = searchStr === '' || 
      p.title.toLowerCase().includes(searchStr) ||
      p.address.toLowerCase().includes(searchStr) ||
      p.city.toLowerCase().includes(searchStr);

    const matchesType = typeFilter === 'all' || p.type === typeFilter;
    const matchesStatus = statusFilter === 'all' || p.status === statusFilter;

    return matchesSearch && matchesType && matchesStatus;
  });
</script>

<div class="view-section active">
  <div class="actions-bar">
    <div class="filters-wrap">
      <select bind:value={typeFilter} class="form-control" style="width: 140px; border-radius: 8px; cursor: pointer;">
        <option value="all">All Types</option>
        <option value="flat">Flat / Apartment</option>
        <option value="villa">House / Villa</option>
        <option value="commercial">Commercial</option>
        <option value="studio">Studio Room</option>
      </select>
      <select bind:value={statusFilter} class="form-control" style="width: 140px; border-radius: 8px; cursor: pointer;">
        <option value="all">All Statuses</option>
        <option value="vacant">Vacant</option>
        <option value="occupied">Occupied</option>
        <option value="maintenance">Maintenance</option>
      </select>
    </div>
    {#if user && (user.role === 'admin' || user.role === 'manager')}
      <button class="topbar-btn primary" on:click={openAddModal}><i class="ti ti-plus"></i> Add Property</button>
    {/if}
  </div>

  {#if loading}
    <div style="padding:40px; text-align:center; color:var(--text-secondary)">Loading property list...</div>
  {:else if filteredProperties.length === 0}
    <div style="padding:40px; text-align:center; color:var(--text-secondary)">No properties found.</div>
  {:else}
    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 24px;">
      {#each filteredProperties as p}
        <!-- Card -->
        <div class="property-item-card" on:click={() => openDetails(p)} style="background:var(--bg-primary); border:1px solid var(--border-primary); border-radius:var(--radius-lg); overflow:hidden; box-shadow:var(--shadow-sm); cursor:pointer; display:flex; flex-direction:column; position:relative; transition:var(--transition);">
          
          <!-- Image -->
          <div style="position:relative; height:180px; overflow:hidden;">
            <img src={p.image_url} alt={p.title} style="width:100%; height:100%; object-fit:cover;">
            <span class="prop-status status-{p.status}" style="position:absolute; top:12px; right:12px;">{p.status}</span>
          </div>

          <!-- Horizontal thumbnail scroll gallery (Item 7 Requirement) -->
          {#if getCardImages(p).length > 1}
            <div class="horizontal-thumbnail-scroll" on:click|stopPropagation style="display:flex; gap:6px; overflow-x:auto; padding:8px; background:var(--bg-secondary); border-bottom:1px solid var(--border-primary);">
              {#each getCardImages(p) as img}
                <img 
                  src={img} 
                  alt="preview" 
                  style="width:50px; height:38px; border-radius:4px; object-fit:cover; flex-shrink:0; cursor:default; opacity:0.85;"
                >
              {/each}
            </div>
          {/if}

          <!-- Info -->
          <div style="padding:16px; flex:1; display:flex; flex-direction:column;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
              <span style="font-size:11px; text-transform:uppercase; color:var(--text-tertiary); font-weight:700;">{p.type}</span>
              <span style="font-family:var(--font-heading); font-size:16px; font-weight:700; color:var(--primary);">{formatCurrency(p.rent_amount)}/mo</span>
            </div>
            <h4 style="font-family:var(--font-heading); font-size:15px; font-weight:700; color:var(--text-primary); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; margin-bottom:4px;">{p.title}</h4>
            <p style="font-size:12px; color:var(--text-secondary); margin-bottom:12px; display:flex; align-items:center; gap:4px;">
              <i class="ti ti-map-pin"></i> {p.address}, {p.city}
            </p>

            <div style="display:flex; gap:12px; font-size:11px; color:var(--text-tertiary); border-top:1px solid var(--border-tertiary); padding-top:10px; margin-top:auto;">
              {#if p.bedrooms}<span><i class="ti ti-bed"></i> {p.bedrooms} Beds</span>{/if}
              {#if p.bathrooms}<span><i class="ti ti-bath"></i> {p.bathrooms} Baths</span>{/if}
            </div>
            
            {#if user && (user.role === 'admin' || p.manager_id === user.id)}
              <div style="display:flex; gap:8px; margin-top:12px; border-top:1px solid var(--border-tertiary); padding-top:10px;">
                <button class="topbar-btn" on:click={(e) => openEditModal(p, e)} style="flex:1; font-size:11px; padding:4px; justify-content:center;"><i class="ti ti-edit"></i> Edit</button>
                <button class="topbar-btn" on:click={(e) => handleDeleteProperty(p, e)} style="flex:1; font-size:11px; padding:4px; justify-content:center; color:var(--danger); border-color:var(--danger-bg);"><i class="ti ti-trash"></i> Delete</button>
              </div>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<!-- =========================
     VIEW DETAILS MODAL
     ========================= -->
{#if showDetailsModal && selectedProperty}
  <div class="modal-overlay active" on:click={closeDetails}>
    <div class="modal" on:click|stopPropagation style="max-width: 600px;">
      <div class="modal-header">
        <h2 class="modal-title">{selectedProperty.title}</h2>
        <button class="modal-close" on:click={closeDetails}><i class="ti ti-x"></i></button>
      </div>
      <div class="modal-body" style="padding: 20px;">
        
        <!-- Gallery Slider -->
        <div class="prop-gallery-container" style="margin-bottom: 20px;">
          <img src={getCardImages(selectedProperty)[activeDetailsIdx]} class="prop-gallery-main" alt="interior main" style="width:100%; height:240px; border-radius:8px; object-fit:cover;">
          {#if getCardImages(selectedProperty).length > 1}
            <div class="prop-gallery-thumbs" style="display:flex; gap:6px; overflow-x:auto;">
              {#each getCardImages(selectedProperty) as img, idx}
                <img 
                  src={img} 
                  alt="thumb"
                  class="prop-gallery-thumb {activeDetailsIdx === idx ? 'active' : ''}" 
                  on:click={() => activeDetailsIdx = idx}
                  style="width:52px; height:40px; border-radius:4px; object-fit:cover; cursor:pointer; border:2px solid {activeDetailsIdx === idx ? 'var(--primary)' : 'transparent'}; opacity: {activeDetailsIdx === idx ? 1 : 0.6}"
                >
              {/each}
            </div>
          {/if}
        </div>

        <!-- Specifications -->
        <div class="spec-grid">
          <div class="spec-item">
            <span class="spec-label">TYPE</span>
            <span class="spec-value">{selectedProperty.type}</span>
          </div>
          <div class="spec-item">
            <span class="spec-label">RENT</span>
            <span class="spec-value">{formatCurrency(selectedProperty.rent_amount)}/mo</span>
          </div>
          <div class="spec-item">
            <span class="spec-label">STATUS</span>
            <span class="spec-value">{selectedProperty.status}</span>
          </div>
        </div>

        <div style="font-size:13px; color:var(--text-secondary); line-height:1.5; margin-bottom:20px;">
          <strong>Description:</strong> {selectedProperty.description || 'No description provided.'}
        </div>

        <!-- Owner info (Only managers and admins) -->
        {#if user && (user.role === 'admin' || user.role === 'manager')}
          <div style="background:var(--bg-secondary); border:1px solid var(--border-primary); padding:14px; border-radius:8px; margin-bottom:20px;">
            <h4 style="font-size:12px; font-weight:700; color:var(--text-primary); text-transform:uppercase; margin-bottom:8px;"><i class="ti ti-user-shield"></i> Owner Information</h4>
            <div style="font-size:12.5px; color:var(--text-secondary); display:grid; grid-template-columns:1fr 1fr; gap:8px;">
              <div><strong>Name:</strong> {selectedProperty.owner_name || '—'}</div>
              <div><strong>Phone:</strong> {selectedProperty.owner_phone || '—'}</div>
              <div style="grid-column: span 2;"><strong>Email:</strong> {selectedProperty.owner_email || '—'}</div>
            </div>
          </div>
        {/if}

        <!-- Reviews log -->
        <div style="border-top:1px solid var(--border-tertiary); padding-top:15px; margin-top:15px;">
          <h4 style="font-family:var(--font-heading); font-size:14px; font-weight:700; color:var(--text-primary); margin-bottom:10px;">Reviews & Ratings</h4>
          
          {#if user && user.role === 'tenant'}
            <!-- Write Review Form -->
            <form on:submit|preventDefault={handleSubmitReview} style="margin-bottom:15px; padding:12px; background:var(--bg-secondary); border-radius:8px;">
              <div class="form-group" style="margin-bottom:8px;">
                <label class="form-label" for="rating">My Rating</label>
                <select id="rating" bind:value={ratingValue} class="form-control" style="width:100px; height:32px; padding:4px 8px;">
                  <option value={5}>⭐⭐⭐⭐⭐ (5)</option>
                  <option value={4}>⭐⭐⭐⭐ (4)</option>
                  <option value={3}>⭐⭐⭐ (3)</option>
                  <option value={2}>⭐⭐ (2)</option>
                  <option value={1}>⭐ (1)</option>
                </select>
              </div>
              <div class="form-group" style="margin-bottom:10px;">
                <label class="form-label" for="comment">Review Comment</label>
                <textarea id="comment" bind:value={reviewComment} class="form-control" rows="2" placeholder="Write your experience..." required></textarea>
              </div>
              <button type="submit" class="topbar-btn primary" style="font-size:11px; padding:4px 12px;">Submit Review</button>
            </form>
          {/if}

          <div style="display:flex; flex-direction:column; gap:8px; max-height:160px; overflow-y:auto; padding-right:4px;">
            {#if reviews.length === 0}
              <div style="font-size:12px; color:var(--text-secondary); text-align:center; padding:10px;">No reviews yet.</div>
            {:else}
              {#each reviews as rev}
                <div style="padding:10px; background:var(--bg-secondary); border-radius:6px; border-left:2px solid var(--primary);">
                  <div style="display:flex; justify-content:space-between; font-size:11px; font-weight:700; color:var(--text-primary);">
                    <span>{rev.tenant_name}</span>
                    <span style="color:#fbbf24">{'⭐'.repeat(rev.rating)}</span>
                  </div>
                  <p style="font-size:12px; color:var(--text-secondary); margin-top:4px;">{rev.comment}</p>
                </div>
              {/each}
            {/if}
          </div>
        </div>

      </div>
      <div class="modal-footer">
        <button class="topbar-btn" on:click={closeDetails}>Close</button>
        {#if user && user.role === 'tenant' && selectedProperty.status === 'vacant'}
          <button class="topbar-btn primary" on:click={() => handleBookNow(selectedProperty)}>Book Property Now</button>
        {/if}
      </div>
    </div>
  </div>
{/if}

<!-- =========================
     ADD/EDIT PROPERTY MODAL
     ========================= -->
{#if showPropertyModal}
  <div class="modal-overlay active" on:click={() => showPropertyModal = false}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h2 class="modal-title">{editMode ? 'Edit Property Specifications' : 'Register New Property'}</h2>
        <button class="modal-close" on:click={() => showPropertyModal = false}><i class="ti ti-x"></i></button>
      </div>
      <form on:submit={handlePropertySubmit}>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label" for="title">Property Title</label>
            <input type="text" id="title" bind:value={propTitle} class="form-control" placeholder="Sunrise Apartments B-204" required>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label class="form-label" for="address">Address Location</label>
              <input type="text" id="address" bind:value={propAddress} class="form-control" placeholder="Koregaon Park" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="city">City</label>
              <input type="text" id="city" bind:value={propCity} class="form-control" placeholder="Pune" required>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label" for="state">State</label>
              <input type="text" id="state" bind:value={propState} class="form-control" placeholder="Maharashtra">
            </div>
            <div class="form-group">
              <label class="form-label" for="pincode">Pincode</label>
              <input type="text" id="pincode" bind:value={propPincode} class="form-control" placeholder="411001">
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label" for="type">Property Type</label>
              <select id="type" bind:value={propType} class="form-control" required>
                <option value="flat">Flat / Apartment</option>
                <option value="villa">House / Villa</option>
                <option value="commercial">Commercial</option>
                <option value="studio">Studio Room</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label" for="rent">Monthly Rent (₹)</label>
              <input type="number" id="rent" bind:value={propRent} class="form-control" placeholder="28000" min="0" required>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label" for="bedrooms">Bedrooms</label>
              <input type="number" id="bedrooms" bind:value={propBedrooms} class="form-control" placeholder="2" min="0">
            </div>
            <div class="form-group">
              <label class="form-label" for="bathrooms">Bathrooms</label>
              <input type="number" id="bathrooms" bind:value={propBathrooms} class="form-control" placeholder="2" min="0">
            </div>
          </div>

          <div class="form-group">
            <label class="form-label" for="status">Property Status</label>
            <select id="status" bind:value={propStatus} class="form-control" required>
              <option value="vacant">Vacant</option>
              <option value="occupied">Occupied</option>
              <option value="maintenance">Maintenance</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label" for="imageUrl">Main Image URL</label>
            <input type="text" id="imageUrl" bind:value={propImageUrl} class="form-control" placeholder="https://unsplash.com/...">
          </div>

          <!-- Comma-separated list for interior images -->
          <div class="form-group">
            <label class="form-label" for="interiorImages">Interior Images URLs (Comma-separated)</label>
            <textarea id="interiorImages" bind:value={propInteriorImages} class="form-control" rows="2" placeholder="URL1, URL2, URL3..."></textarea>
          </div>

          <!-- Owner specifications (Item 8 Requirement) -->
          <div style="border-top:1px dashed var(--border-secondary); padding-top:12px; margin-top:12px;">
            <h4 style="font-size:12px; font-weight:700; color:var(--primary); text-transform:uppercase; margin-bottom:8px;">Property Owner / Landlord Details</h4>
            
            <div class="form-group">
              <label class="form-label" for="ownerName">Owner Name</label>
              <input type="text" id="ownerName" bind:value={propOwnerName} class="form-control" placeholder="Landlord Ramesh">
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label" for="ownerEmail">Owner Email</label>
                <input type="email" id="ownerEmail" bind:value={propOwnerEmail} class="form-control" placeholder="ramesh@example.com">
              </div>
              <div class="form-group">
                <label class="form-label" for="ownerPhone">Owner Phone</label>
                <input type="text" id="ownerPhone" bind:value={propOwnerPhone} class="form-control" placeholder="+91 99887 76655">
              </div>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label" for="desc">Description Notes</label>
            <textarea id="desc" bind:value={propDesc} class="form-control" rows="2" placeholder="Parking, balcony view, nearby transport..."></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="topbar-btn" on:click={() => showPropertyModal = false}>Cancel</button>
          <button type="submit" class="topbar-btn primary">Save Specifications</button>
        </div>
      </form>
    </div>
  </div>
{/if}

<style>
  .property-item-card:hover {
    transform: translateY(-2px);
    border-color: var(--border-secondary) !important;
    box-shadow: var(--shadow-md) !important;
  }
  
  /* Scrollbar customization for thumb preview scroll */
  .horizontal-thumbnail-scroll::-webkit-scrollbar {
    height: 4px;
  }
  .horizontal-thumbnail-scroll::-webkit-scrollbar-thumb {
    background: var(--border-secondary);
    border-radius: 2px;
  }
</style>
