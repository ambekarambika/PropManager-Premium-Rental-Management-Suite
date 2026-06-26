<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import * as api from '../lib/api.js';
  import { formatCurrency } from '../lib/utils.js';

  const dispatch = createEventDispatcher();

  let properties = [];
  let loading = true;
  let searchTerm = '';
  let selectedType = 'all';
  let selectedRent = 'all';

  // Stats mock data for rendering
  const stats = [
    { value: '1,200+', label: 'Premium Properties' },
    { value: '99.4%', label: 'Occupancy Rate' },
    { value: '₹1.5Cr+', label: 'Rent Transacted' },
    { value: '24/7', label: 'Digital Support' }
  ];

  // Features list for bento grid
  const keyFeatures = [
    {
      title: 'Smart Digital Leases',
      desc: 'Formulate, customize, and sign legally-compliant lease agreements in under 60 seconds completely online.',
      icon: 'ti-file-pencil',
      badge: 'Seamless Onboarding',
      gridClass: 'col-span-8'
    },
    {
      title: 'Direct Maintenance Dispatch',
      desc: 'Report tenant leaks or electrical issues directly with visual photos and track plumber dispatch status in real-time.',
      icon: 'ti-tool',
      badge: 'Zero Delay',
      gridClass: 'col-span-4'
    },
    {
      title: 'Automated Rent Ledger',
      desc: 'Landlords and tenants view clear digital receipts. Monthly rent invoices are auto-generated and matched.',
      icon: 'ti-receipt',
      badge: 'Direct Payments',
      gridClass: 'col-span-4'
    },
    {
      title: 'Deep Analytics Engine',
      desc: 'Gain high-fidelity insights on portfolio revenue growth, occupancy statistics trends, and upcoming agreement renewals via dynamic data visualization.',
      icon: 'ti-chart-line',
      badge: 'For Owners & Managers',
      gridClass: 'col-span-8'
    }
  ];

  onMount(async () => {
    await loadProperties();
  });

  async function loadProperties() {
    try {
      loading = true;
      properties = await api.getProperties({ status: 'vacant' });
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  }

  function handleSignIn() {
    dispatch('login-click');
  }

  function scrollToExplore() {
    const element = document.getElementById('explore-section');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  }

  function handleViewDetails(propertyId) {
    dispatch('view-details', { propertyId });
  }

  $: filteredProperties = properties.filter(p => {
    const matchesSearch = searchTerm === '' || 
      p.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.address.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.city.toLowerCase().includes(searchTerm.toLowerCase());
      
    const matchesType = selectedType === 'all' || p.type === selectedType;
    
    let matchesRent = true;
    if (selectedRent === '0-15000') matchesRent = p.rent_amount < 15000;
    else if (selectedRent === '15000-30000') matchesRent = p.rent_amount >= 15000 && p.rent_amount <= 30000;
    else if (selectedRent === '30000-50000') matchesRent = p.rent_amount >= 30000 && p.rent_amount <= 50000;
    else if (selectedRent === '50000+') matchesRent = p.rent_amount > 50000;

    return matchesSearch && matchesType && matchesRent;
  });
</script>

<div class="landing-page-root">
  <!-- Glowing Background Orbs with slow float animations -->
  <div class="glow-ball glow-ball-orange"></div>
  <div class="glow-ball glow-ball-purple"></div>
  <div class="glow-ball glow-ball-blue"></div>

  <!-- Header Section with blur glassmorphism -->
  <header class="landing-header">
    <div class="logo-mark" style="display: flex; align-items: center; gap: 12px; cursor: pointer;" on:click={() => window.scrollTo({top: 0, behavior: 'smooth'})}>
      <div class="logo-icon" style="background: linear-gradient(135deg, #FF6B35 0%, #FFA800 100%); color: #fff; width: 44px; height: 44px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 24px; box-shadow: 0 4px 20px rgba(255, 107, 53, 0.4);">
        <i class="ti ti-building"></i>
      </div>
      <div>
        <div class="logo-text" style="font-family: var(--font-heading); font-weight: 800; font-size: 22px; color: #0F172A; letter-spacing: -0.8px;">PropManager</div>
        <div class="logo-sub" style="font-size: 9.5px; color: #FF6B35; font-weight: 800; text-transform: uppercase; letter-spacing: 2px;">Premium Suite</div>
      </div>
    </div>
    <div style="display: flex; align-items: center; gap: 32px;">
      <span class="nav-link" on:click={scrollToExplore}>Explore Properties</span>
      <button type="button" class="explore-btn" on:click={handleSignIn}>
        <i class="ti ti-login" style="font-size: 16px;"></i> Sign In
      </button>
    </div>
  </header>

  <!-- Hero Section -->
  <section class="hero-section">
    <div class="hero-grid-container">
      <!-- Hero Copy -->
      <div class="hero-text-block">
        <span class="hero-badge">
          <span class="pulse-dot-orange"></span>
          Elegant Rental Management Suite
        </span>
        <h1>
          Find Your Next <br> <span class="gradient-text">Perfect Space</span>
        </h1>
        <p class="hero-desc">
          Experience next-generation rental housing. Explore flats, luxury villas, and premium commercial spaces with instant digital leases and automated paperless invoicing.
        </p>

        <!-- Stats row inside Hero -->
        <div class="stats-row">
          {#each stats as stat}
            <div class="stat-badge-card">
              <span class="stat-value">{stat.value}</span>
              <span class="stat-label">{stat.label}</span>
            </div>
          {/each}
        </div>

        <!-- Integrated Search Widget Capsule -->
        <div class="search-widget-capsule">
          <div class="search-input-field">
            <i class="ti ti-search search-icon"></i>
            <input type="text" bind:value={searchTerm} class="widget-input" placeholder="Search by name, city or location...">
          </div>
          <div class="widget-divider"></div>
          <div class="search-select-field">
            <i class="ti ti-home select-icon"></i>
            <select bind:value={selectedType} class="widget-select">
              <option value="all">Any Type</option>
              <option value="flat">Flats</option>
              <option value="villa">Villas</option>
              <option value="commercial">Commercial</option>
              <option value="studio">Studios</option>
            </select>
          </div>
          <div class="widget-divider"></div>
          <div class="search-select-field">
            <i class="ti ti-currency-rupee select-icon"></i>
            <select bind:value={selectedRent} class="widget-select">
              <option value="all">Any Budget</option>
              <option value="0-15000">Under ₹15K/mo</option>
              <option value="15000-30000">₹15K - ₹30K/mo</option>
              <option value="30000-50000">₹30K - ₹50K/mo</option>
              <option value="50000+">₹50K+/mo</option>
            </select>
          </div>
          <button type="button" class="search-action-btn" on:click={scrollToExplore}>
            Search
          </button>
        </div>
      </div>

      <!-- Hero Visual (Overlapping Premium Picture and glass lease agreement card) -->
      <div class="hero-mockup-wrapper">
        <!-- Picture element -->
        <div class="hero-image-container">
          <img src="/hero_house.png" alt="Luxury Modern Villa" class="hero-house-image">
          <div class="hero-image-overlay"></div>
        </div>

        <!-- Overlapping Glass lease card -->
        <div class="glass-mockup-card-overlay">
          <div class="mockup-header">
            <div class="mockup-indicator">
              <span class="pulse-green-dot"></span> Smart Digital Lease
            </div>
            <div class="mockup-id">AGR-2026-78A</div>
          </div>
          
          <div class="mockup-body">
            <div class="mockup-meta-row">
              <div class="meta-label">LEASING PROPERTY</div>
              <div class="meta-value">Sunrise Apartments, Unit B-204</div>
            </div>
            
            <div class="mockup-meta-row">
              <div class="meta-label">MONTHLY RENT</div>
              <div class="meta-value text-orange">₹28,500 <span class="rent-label">/ month</span></div>
            </div>

            <div class="mockup-signatures">
              <div class="sig-block">
                <span class="sig-label">LANDLORD</span>
                <span class="sig-font font-orange">Rajesh Kumar</span>
              </div>
              <div class="sig-divider"></div>
              <div class="sig-block">
                <span class="sig-label">TENANT</span>
                <span class="sig-font font-purple">Priya Desai</span>
              </div>
            </div>

            <div class="mockup-badge-verified">
              <i class="ti ti-shield-check"></i> SECURE CRYPTO-SIGNED
            </div>
          </div>
        </div>

        <!-- Floating mini payment status card -->
        <div class="floating-mini-status-light">
          <div class="mini-icon-status">
            <i class="ti ti-cash"></i>
          </div>
          <div>
            <div class="mini-label">Ledger Rent Status</div>
            <div class="mini-value">₹28,500 Paid <span class="mini-badge-success">Cleared</span></div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="scroll-prompt" on:click={scrollToExplore}>
      <span style="font-size: 11px; font-weight: 700; letter-spacing: 2px; color: #475569; text-transform: uppercase;">Explore Portfolio</span>
      <i class="ti ti-chevron-down scroll-arrow"></i>
    </div>
  </section>

  <!-- Key Features Bento Grid Section -->
  <section class="features-section">
    <div class="section-title-wrapper">
      <span class="section-badge">Premium Framework</span>
      <h2 class="section-title">Designed for Visual & Operational Excellence</h2>
      <p class="section-subtitle">We remove the friction from traditional property management operations using smart automated workflows.</p>
    </div>

    <div class="bento-grid">
      {#each keyFeatures as feat}
        <div class="bento-item {feat.gridClass}">
          <div class="bento-card-bg-gradient"></div>
          <div style="position: relative; z-index: 5;">
            <div class="bento-header-row">
              <div class="bento-icon-wrapper">
                <i class="ti {feat.icon}"></i>
              </div>
              <span class="bento-badge">{feat.badge}</span>
            </div>
            <h3 class="bento-card-title">{feat.title}</h3>
            <p class="bento-card-desc">{feat.desc}</p>
          </div>
        </div>
      {/each}
    </div>
  </section>

  <!-- Vacant Properties Section -->
  <section class="public-properties-section" id="explore-section">
    <div class="section-title-wrapper">
      <span class="section-badge">Live Portfolios</span>
      <h2 class="section-title">Explore Premium Vacant Spaces</h2>
      <p class="section-subtitle">Browse through carefully vetted apartments, flats, and estates with virtual walkthroughs and detailed reviews.</p>
    </div>

    <!-- Category filter tabs for properties -->
    <div class="category-tabs-container">
      {#each ['all', 'flat', 'villa', 'commercial', 'studio'] as type}
        <button 
          type="button" 
          class="category-tab {selectedType === type ? 'active' : ''}" 
          on:click={() => selectedType = type}
        >
          <i class="ti {type === 'all' ? 'ti-apps' : type === 'flat' ? 'ti-building' : type === 'villa' ? 'ti-home' : type === 'commercial' ? 'ti-building-store' : 'ti-layout-grid'}"></i>
          <span>{type === 'all' ? 'All Types' : type.charAt(0).toUpperCase() + type.slice(1) + 's'}</span>
        </button>
      {/each}
    </div>

    {#if loading}
      <div class="loading-wrapper-state">
        <i class="ti ti-loader animate-spin spin-orange"></i>
        <div>Fetching vacant premium portfolios...</div>
      </div>
    {:else if filteredProperties.length === 0}
      <div class="no-properties-box">
        <i class="ti ti-home-off no-prop-icon"></i>
        <h4>No Vetted Spaces Match Your Search</h4>
        <p>Try resetting the search terms, selected property type, or budget constraints.</p>
        <button class="reset-filters-btn" on:click={() => { searchTerm = ''; selectedType = 'all'; selectedRent = 'all'; }}>
          Reset All Filters
        </button>
      </div>
    {:else}
      <div class="public-properties-grid">
        {#each filteredProperties as p}
          <div class="prop-card-public">
            <div class="pub-prop-img-wrapper">
              <img src={p.image_url} alt={p.title} class="property-image">
              <div class="property-card-overlay-gradient"></div>
              <span class="prop-badge-type">{p.type}</span>
              {#if p.interior_images}
                <div class="photo-count-badge">
                  <i class="ti ti-photo"></i> {p.interior_images.split(',').length + 1} Photos
                </div>
              {/if}
            </div>

            <div class="property-card-body">
              <div class="price-header-row">
                <span class="prop-rent-display">
                  {formatCurrency(p.rent_amount)}<span class="rent-period-label">/mo</span>
                </span>
                <span class="rent-deposit-badge">Deposit: {formatCurrency(p.rent_amount * 2)}</span>
              </div>
              <h3 class="property-card-title">{p.title}</h3>
              <p class="property-card-address">
                <i class="ti ti-map-pin pin-color"></i> {p.address}, {p.city}
              </p>
              
              <div class="spec-row">
                {#if p.bedrooms}
                  <span class="spec-item"><i class="ti ti-bed"></i> {p.bedrooms} Beds</span>
                {/if}
                {#if p.bathrooms}
                  <span class="spec-item"><i class="ti ti-bath"></i> {p.bathrooms} Baths</span>
                {/if}
                <span class="spec-item"><i class="ti ti-arrows-maximize"></i> 1,450 sqft</span>
              </div>

              <button type="button" class="view-details-btn" on:click={() => handleViewDetails(p.id)}>
                View Specifications & Reviews <i class="ti ti-arrow-right" style="margin-left: 6px;"></i>
              </button>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </section>

  <!-- Premium Testimonials Section -->
  <section class="testimonials-section">
    <div class="section-title-wrapper">
      <span class="section-badge">Client Stories</span>
      <h2 class="section-title">Vouched by Happy Landlords & Residents</h2>
      <p class="section-subtitle">Real feedback from users who digitized their housing contracts and payments.</p>
    </div>
    <div class="testimonials-grid">
      <div class="testimonial-card">
        <div class="testimonial-header">
          <div class="testimonial-stars">
            <i class="ti ti-star-filled"></i><i class="ti ti-star-filled"></i><i class="ti ti-star-filled"></i><i class="ti ti-star-filled"></i><i class="ti ti-star-filled"></i>
          </div>
          <i class="ti ti-quote quote-icon"></i>
        </div>
        <p class="testimonial-quote">"Renting Sunrise Apartments B-204 has been amazing. The app makes paying rent and reporting maintenance requests so simple. Landlord Rajesh resolved my bathroom plumbing on the same day!"</p>
        <div class="testimonial-author">
          <div class="testimonial-avatar avatar-orange">AS</div>
          <div>
            <div class="author-name">Arjun Sharma</div>
            <div class="author-sub">Resident at Koregaon Park</div>
          </div>
        </div>
      </div>
      
      <div class="testimonial-card">
        <div class="testimonial-header">
          <div class="testimonial-stars">
            <i class="ti ti-star-filled"></i><i class="ti ti-star-filled"></i><i class="ti ti-star-filled"></i><i class="ti ti-star-filled"></i><i class="ti ti-star-filled"></i>
          </div>
          <i class="ti ti-quote quote-icon"></i>
        </div>
        <p class="testimonial-quote">"The Green Valley Villa 7A is wonderful. Whenever we have electrical line issues, Manager Rajesh assigns an electrician slots immediately through the portal. Outstanding service."</p>
        <div class="testimonial-author">
          <div class="testimonial-avatar avatar-purple">PD</div>
          <div>
            <div class="author-name">Priya Desai</div>
            <div class="author-sub">Resident at Baner Hills</div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Glowing CTA Banner Section -->
  <section class="cta-banner-section">
    <div class="cta-card">
      <div class="cta-card-glow"></div>
      <div style="position: relative; z-index: 5;">
        <span class="cta-badge">Instant Access</span>
        <h3>Ready to Step Into the Future of Renting?</h3>
        <p>Digitize your leases, automate monthly invoice notifications, and manage maintenance directly from our unified suite.</p>
        <div class="cta-actions">
          <button class="cta-action-primary" on:click={handleSignIn}>
            <i class="ti ti-rocket"></i> Access Dashboard Now
          </button>
          <button class="cta-action-secondary" on:click={scrollToExplore}>
            Browse Vacancies
          </button>
        </div>
      </div>
    </div>
  </section>

  <!-- Footer -->
  <footer class="landing-footer">
    <div class="footer-container">
      <div class="footer-brand-column">
        <div class="logo-mark" style="display: flex; align-items: center; gap: 10px; margin-bottom: 16px;">
          <div class="logo-icon" style="background: linear-gradient(135deg, #FF6B35 0%, #FFA800 100%); color: #fff; width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px;">
            <i class="ti ti-building"></i>
          </div>
          <div>
            <div class="logo-text" style="font-family: var(--font-heading); font-weight: 800; font-size: 18px; color: #0F172A; letter-spacing: -0.5px;">PropManager</div>
            <div class="logo-sub" style="font-size: 8.5px; color: #FF6B35; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px;">Premium Suite</div>
          </div>
        </div>
        <p class="footer-brand-desc">A unified cloud rental ledger, smart lease management, and immediate service dispatch dashboard.</p>
        <div class="footer-socials">
          <i class="ti ti-brand-twitter"></i>
          <i class="ti ti-brand-linkedin"></i>
          <i class="ti ti-brand-github"></i>
        </div>
      </div>
      
      <div class="footer-links-column">
        <h4>Technology</h4>
        <span class="footer-link">Vite & Svelte 5</span>
        <span class="footer-link">FastAPI Python API</span>
        <span class="footer-link">PostgreSQL Database</span>
        <span class="footer-link">Glassmorphic Architecture</span>
      </div>

      <div class="footer-links-column">
        <h4>Product Features</h4>
        <span class="footer-link">Smart Electronic Leases</span>
        <span class="footer-link">Real-time ledger matching</span>
        <span class="footer-link">Service dispatch log</span>
        <span class="footer-link">Tenant feedback ratings</span>
      </div>
    </div>
    
    <div class="footer-bottom">
      <p>© 2026 PropManager Premium Rental Suite. All rights reserved.</p>
      <p>Secure SSL Encrypted Platform Connection</p>
    </div>
  </footer>
</div>

<style>
  /* Base Layout Styling - Light Clean Mode */
  .landing-page-root {
    min-height: 100vh;
    background-color: #ffffff;
    overflow-y: auto;
    height: 100vh;
    color: #0F172A;
    position: relative;
    font-family: var(--font-sans);
  }

  /* Beautiful Floating Radial Gradient Glow Orbs (Soft opacities for light background) */
  .glow-ball {
    position: absolute;
    border-radius: 50%;
    filter: blur(140px);
    pointer-events: none;
    z-index: 0;
    opacity: 0.35;
  }
  .glow-ball-orange {
    width: 450px;
    height: 450px;
    background: radial-gradient(circle, rgba(255, 107, 53, 0.16) 0%, rgba(255, 107, 53, 0) 70%);
    top: -100px;
    left: -100px;
    animation: orbFloat 20s ease-in-out infinite alternate;
  }
  .glow-ball-purple {
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(124, 58, 237, 0.1) 0%, rgba(124, 58, 237, 0) 70%);
    top: 250px;
    right: -150px;
    animation: orbFloat 25s ease-in-out infinite alternate-reverse;
  }
  .glow-ball-blue {
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(24, 95, 165, 0.08) 0%, rgba(24, 95, 165, 0) 70%);
    bottom: 200px;
    left: 20%;
    animation: orbFloat 18s ease-in-out infinite alternate;
  }

  @keyframes orbFloat {
    0% { transform: translateY(0) scale(1); }
    100% { transform: translateY(-40px) scale(1.1); }
  }

  /* Header Sticky styling */
  .landing-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 80px;
    background: rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border-bottom: 1px solid rgba(15, 23, 42, 0.05);
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .nav-link {
    font-size: 14.5px;
    font-weight: 600;
    color: #475569;
    cursor: pointer;
    transition: color 0.3s;
  }
  .nav-link:hover {
    color: #FF6B35;
  }

  .explore-btn {
    background: linear-gradient(135deg, #FF6B35 0%, #FFA800 100%);
    border: none;
    color: white;
    font-weight: 700;
    border-radius: 30px;
    padding: 12px 28px;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
    box-shadow: 0 4px 15px rgba(255, 107, 53, 0.2);
    transition: transform 0.3s, box-shadow 0.3s;
    cursor: pointer;
  }
  .explore-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(255, 107, 53, 0.35);
  }

  /* Hero Section Grid */
  .hero-section {
    position: relative;
    padding: 80px 80px 60px 80px;
    min-height: calc(100vh - 85px);
    display: flex;
    flex-direction: column;
    justify-content: center;
    background: radial-gradient(circle at center, rgba(248, 250, 252, 0.4) 0%, #ffffff 100%);
    z-index: 1;
  }

  .hero-grid-container {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    gap: 60px;
    align-items: center;
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
  }

  .hero-text-block {
    text-align: left;
  }

  .hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(255, 107, 53, 0.05);
    border: 1px solid rgba(255, 107, 53, 0.18);
    color: #E85A24;
    padding: 8px 18px;
    border-radius: 30px;
    font-size: 12.5px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 28px;
  }

  .pulse-dot-orange {
    width: 7px;
    height: 7px;
    background-color: #FF6B35;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 8px #FF6B35;
    animation: pulseGlow 1.5s infinite alternate;
  }

  @keyframes pulseGlow {
    0% { opacity: 0.4; }
    100% { opacity: 1; }
  }

  .hero-text-block h1 {
    font-family: var(--font-heading);
    font-size: 60px;
    font-weight: 900;
    color: #0F172A;
    margin-bottom: 24px;
    line-height: 1.15;
    letter-spacing: -1.8px;
  }

  .gradient-text {
    background: linear-gradient(135deg, #FF6B35 0%, #FFA800 50%, #7C3AED 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: inline-block;
  }

  .hero-desc {
    font-size: 17px;
    color: #475569;
    max-width: 580px;
    line-height: 1.65;
    font-weight: 500;
    margin-bottom: 40px;
  }

  /* Stats row */
  .stats-row {
    display: flex;
    gap: 16px;
    margin-bottom: 44px;
    flex-wrap: wrap;
  }
  .stat-badge-card {
    background: rgba(15, 23, 42, 0.02);
    border: 1px solid rgba(15, 23, 42, 0.05);
    border-radius: 16px;
    padding: 12px 20px;
    display: flex;
    flex-direction: column;
    flex: 1;
    min-width: 120px;
  }
  .stat-value {
    font-family: var(--font-heading);
    font-size: 24px;
    font-weight: 800;
    color: #0F172A;
  }
  .stat-label {
    font-size: 11px;
    color: #475569;
    font-weight: 600;
    margin-top: 4px;
  }

  /* High-end Search Capsule styling */
  .search-widget-capsule {
    background: rgba(255, 255, 255, 0.85);
    border: 1px solid rgba(15, 23, 42, 0.08);
    border-radius: 40px;
    padding: 8px 12px 8px 24px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 20px 50px rgba(15, 23, 42, 0.08);
    width: 100%;
    max-width: 680px;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
  }

  .search-input-field {
    display: flex;
    align-items: center;
    gap: 10px;
    flex: 1.5;
  }

  .search-icon {
    color: #FF6B35;
    font-size: 18px;
  }

  .widget-input {
    background: transparent;
    border: none;
    color: #0F172A;
    font-size: 13.5px;
    width: 100%;
    font-weight: 500;
  }
  .widget-input::placeholder {
    color: #94A3B8;
  }
  .widget-input:focus {
    outline: none;
  }

  .widget-divider {
    width: 1px;
    height: 32px;
    background: rgba(15, 23, 42, 0.08);
  }

  .search-select-field {
    display: flex;
    align-items: center;
    gap: 8px;
    flex: 1;
  }

  .select-icon {
    color: #64748B;
    font-size: 15px;
  }

  .widget-select {
    background: transparent;
    border: none;
    color: #0F172A;
    font-size: 13.5px;
    cursor: pointer;
    font-weight: 600;
    width: 100%;
    padding: 4px 10px 4px 0;
  }
  .widget-select:focus {
    outline: none;
  }
  .widget-select option {
    background: #ffffff;
    color: #0f172a;
    padding: 8px;
  }

  .search-action-btn {
    background: linear-gradient(135deg, #FF6B35 0%, #FFA800 100%);
    border: none;
    color: white;
    font-weight: 700;
    border-radius: 30px;
    padding: 10px 24px;
    font-size: 13.5px;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(255, 107, 53, 0.2);
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .search-action-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 20px rgba(255, 107, 53, 0.35);
  }

  /* Interactive Premium Picture container overlay */
  .hero-mockup-wrapper {
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .hero-image-container {
    width: 100%;
    max-width: 480px;
    height: 400px;
    border-radius: 28px;
    overflow: hidden;
    position: relative;
    box-shadow: 0 30px 60px rgba(15, 23, 42, 0.12);
    border: 4px solid #ffffff;
  }

  .hero-house-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
  }
  .hero-image-container:hover .hero-house-image {
    transform: scale(1.04);
  }

  .hero-image-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, rgba(255, 107, 53, 0.05) 0%, rgba(124, 58, 237, 0.05) 100%);
    pointer-events: none;
  }

  /* Floating glass contract overlapping the image */
  .glass-mockup-card-overlay {
    position: absolute;
    top: -20px;
    left: -30px;
    background: rgba(255, 255, 255, 0.85);
    border: 1px solid rgba(15, 23, 42, 0.06);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 24px;
    padding: 24px;
    width: 100%;
    max-width: 320px;
    box-shadow: 0 25px 50px rgba(15, 23, 42, 0.15);
    z-index: 10;
    animation: floatCardOverlay 6s ease-in-out infinite alternate;
  }

  @keyframes floatCardOverlay {
    0% { transform: translateY(0); }
    100% { transform: translateY(-10px); }
  }

  .mockup-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(15, 23, 42, 0.06);
    padding-bottom: 12px;
    margin-bottom: 16px;
  }

  .mockup-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #10B981;
  }

  .pulse-green-dot {
    width: 8px;
    height: 8px;
    background-color: #10B981;
    border-radius: 50%;
    box-shadow: 0 0 10px #10B981;
    animation: pulseGlow 1.2s infinite alternate;
  }

  .mockup-id {
    font-size: 10px;
    color: #64748B;
    font-weight: 700;
  }

  .mockup-meta-row {
    margin-bottom: 12px;
  }

  .meta-label {
    font-size: 8px;
    color: #64748B;
    font-weight: 800;
    letter-spacing: 1.5px;
    margin-bottom: 4px;
  }

  .meta-value {
    font-size: 13.5px;
    font-weight: 700;
    color: #0F172A;
  }

  .text-orange {
    color: #FF6B35;
    font-family: var(--font-heading);
    font-size: 16px;
    font-weight: 800;
  }
  
  .rent-label {
    font-size: 11px;
    font-weight: 500;
    color: #64748B;
  }

  .mockup-signatures {
    display: flex;
    justify-content: space-between;
    background: rgba(15, 23, 42, 0.02);
    border: 1px solid rgba(15, 23, 42, 0.04);
    border-radius: 12px;
    padding: 10px;
    margin-top: 16px;
    margin-bottom: 16px;
    gap: 8px;
  }

  .sig-block {
    display: flex;
    flex-direction: column;
  }

  .sig-label {
    font-size: 7.5px;
    color: #64748B;
    font-weight: 800;
    letter-spacing: 0.8px;
    margin-bottom: 4px;
  }

  .sig-font {
    font-family: 'Outfit', cursive, sans-serif;
    font-size: 12px;
    font-style: italic;
    font-weight: 700;
  }

  .font-orange { color: #FF8454; }
  .font-purple { color: #8B5CF6; }

  .sig-divider {
    width: 1px;
    background: rgba(15, 23, 42, 0.08);
  }

  .mockup-badge-verified {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    background: rgba(16, 185, 129, 0.08);
    border: 1px solid rgba(16, 185, 129, 0.18);
    border-radius: 10px;
    padding: 8px;
    color: #10B981;
    font-size: 9.5px;
    font-weight: 700;
    letter-spacing: 0.5px;
  }

  .floating-mini-status-light {
    position: absolute;
    bottom: -15px;
    right: -20px;
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(15, 23, 42, 0.06);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 20px;
    padding: 14px 18px;
    display: flex;
    align-items: center;
    gap: 12px;
    box-shadow: 0 20px 40px rgba(15, 23, 42, 0.1);
    z-index: 15;
    width: 230px;
    animation: floatCardReverseOverlay 6s ease-in-out infinite alternate;
  }

  @keyframes floatCardReverseOverlay {
    0% { transform: translateY(-8px); }
    100% { transform: translateY(4px); }
  }

  .mini-icon-status {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: rgba(16, 185, 129, 0.1);
    color: #10B981;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
  }

  .mini-label {
    font-size: 9.5px;
    color: #64748B;
    font-weight: 600;
  }

  .mini-value {
    font-size: 12.5px;
    font-weight: 700;
    color: #0F172A;
    margin-top: 2px;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .mini-badge-success {
    font-size: 9px;
    background: #10B981;
    color: #fff;
    padding: 1px 6px;
    border-radius: 8px;
    font-weight: 700;
  }

  .scroll-prompt {
    margin-top: auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    transition: transform 0.2s;
  }
  .scroll-prompt:hover {
    transform: translateY(3px);
  }

  .scroll-arrow {
    font-size: 20px;
    color: #FF6B35;
    animation: bounce 1.5s infinite;
  }

  @keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(5px); }
  }

  /* Common Section Headers */
  .section-title-wrapper {
    text-align: center;
    max-width: 700px;
    margin: 0 auto 64px auto;
  }

  .section-badge {
    font-size: 11px;
    font-weight: 800;
    color: #FF6B35;
    text-transform: uppercase;
    letter-spacing: 2px;
    display: block;
    margin-bottom: 12px;
  }

  .section-title {
    font-family: var(--font-heading);
    font-size: 38px;
    font-weight: 800;
    color: #0F172A;
    letter-spacing: -0.8px;
    line-height: 1.2;
    margin-bottom: 16px;
  }

  .section-subtitle {
    font-size: 15px;
    color: #475569;
    line-height: 1.6;
    font-weight: 500;
  }

  /* Features Bento Grid styling */
  .features-section {
    padding: 120px 80px;
    background: #F8FAFC;
    border-top: 1px solid rgba(15, 23, 42, 0.04);
    position: relative;
    z-index: 5;
  }

  .bento-grid {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    gap: 24px;
    max-width: 1200px;
    margin: 0 auto;
  }

  .bento-item {
    background: rgba(255, 255, 255, 0.85);
    border: 1px solid rgba(15, 23, 42, 0.05);
    border-radius: 24px;
    padding: 36px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    position: relative;
    overflow: hidden;
    transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.4s, box-shadow 0.4s;
    box-shadow: 0 4px 20px rgba(15, 23, 42, 0.02);
  }

  .bento-item:hover {
    transform: translateY(-6px);
    border-color: rgba(255, 107, 53, 0.3);
    box-shadow: 0 15px 35px rgba(255, 107, 53, 0.06);
  }

  .bento-card-bg-gradient {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, rgba(255, 107, 53, 0.03) 0%, rgba(124, 58, 237, 0.02) 100%);
    opacity: 0;
    transition: opacity 0.4s;
    pointer-events: none;
  }

  .bento-item:hover .bento-card-bg-gradient {
    opacity: 1;
  }

  .bento-header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }

  .bento-icon-wrapper {
    width: 48px;
    height: 48px;
    border-radius: 14px;
    background: rgba(255, 107, 53, 0.08);
    border: 1px solid rgba(255, 107, 53, 0.18);
    color: #FF6B35;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
  }

  .bento-badge {
    font-size: 10.5px;
    font-weight: 700;
    color: #64748B;
    background: rgba(15, 23, 42, 0.02);
    border: 1px solid rgba(15, 23, 42, 0.05);
    padding: 4px 10px;
    border-radius: 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .bento-card-title {
    font-family: var(--font-heading);
    font-size: 20px;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 12px;
  }

  .bento-card-desc {
    font-size: 14px;
    color: #475569;
    line-height: 1.6;
    font-weight: 500;
  }

  /* Bento Columns grid maps */
  .col-span-8 { grid-column: span 8; }
  .col-span-4 { grid-column: span 4; }

  @media (max-width: 992px) {
    .col-span-8, .col-span-4 {
      grid-column: span 12;
    }
  }

  /* Properties grid filters tabs */
  .public-properties-section {
    padding: 120px 80px;
    position: relative;
    z-index: 5;
    background: #ffffff;
  }

  .category-tabs-container {
    display: flex;
    justify-content: center;
    gap: 12px;
    margin-bottom: 48px;
    flex-wrap: wrap;
  }

  .category-tab {
    background: rgba(15, 23, 42, 0.03);
    border: 1px solid rgba(15, 23, 42, 0.05);
    border-radius: 30px;
    color: #475569;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  }

  .category-tab:hover {
    color: #0F172A;
    border-color: rgba(15, 23, 42, 0.12);
    background: rgba(15, 23, 42, 0.05);
  }

  .category-tab.active {
    color: #fff;
    background: linear-gradient(135deg, #FF6B35 0%, #FFA800 100%);
    border-color: transparent;
    box-shadow: 0 4px 15px rgba(255, 107, 53, 0.25);
  }

  /* Svelte Properties Loading and No Match UI */
  .loading-wrapper-state {
    text-align: center;
    padding: 80px 0;
    color: #475569;
    font-size: 15px;
  }

  .spin-orange {
    font-size: 36px;
    color: #FF6B35;
    margin-bottom: 12px;
  }

  .no-properties-box {
    text-align: center;
    padding: 80px 40px;
    background: rgba(15, 23, 42, 0.01);
    border-radius: 24px;
    border: 1px dashed rgba(15, 23, 42, 0.08);
    max-width: 600px;
    margin: 0 auto;
  }

  .no-prop-icon {
    font-size: 40px;
    color: #FF6B35;
    margin-bottom: 16px;
  }

  .no-properties-box h4 {
    font-family: var(--font-heading);
    font-size: 18px;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 8px;
  }

  .no-properties-box p {
    font-size: 13.5px;
    color: #475569;
    margin-bottom: 24px;
  }

  .reset-filters-btn {
    background: rgba(15, 23, 42, 0.04);
    border: 1px solid rgba(15, 23, 42, 0.08);
    color: #0F172A;
    font-weight: 600;
    padding: 10px 20px;
    border-radius: 12px;
    font-size: 13.5px;
    cursor: pointer;
    transition: background 0.2s;
  }
  .reset-filters-btn:hover {
    background: rgba(15, 23, 42, 0.08);
  }

  /* Public Premium property grids */
  .public-properties-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
    gap: 32px;
    max-width: 1200px;
    margin: 0 auto;
  }

  .prop-card-public {
    background: #ffffff;
    border: 1px solid rgba(15, 23, 42, 0.05);
    border-radius: 24px;
    overflow: hidden;
    transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.4s, border-color 0.4s;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.03);
  }

  .prop-card-public:hover {
    transform: translateY(-8px);
    border-color: rgba(255, 107, 53, 0.3);
    box-shadow: 0 20px 45px rgba(255, 107, 53, 0.06);
  }

  .pub-prop-img-wrapper {
    position: relative;
    height: 220px;
    overflow: hidden;
  }

  .property-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
  }

  .prop-card-public:hover .property-image {
    transform: scale(1.06);
  }

  .property-card-overlay-gradient {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(to top, rgba(255, 255, 255, 0.25) 0%, rgba(255, 255, 255, 0) 50%);
    pointer-events: none;
  }

  .prop-badge-type {
    position: absolute;
    top: 20px;
    left: 20px;
    background: linear-gradient(135deg, #FF6B35 0%, #FFA800 100%);
    color: white;
    font-size: 10px;
    font-weight: 800;
    padding: 5px 12px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    box-shadow: 0 4px 10px rgba(255, 107, 53, 0.2);
  }

  .photo-count-badge {
    position: absolute;
    bottom: 16px;
    right: 20px;
    background: rgba(255, 255, 255, 0.85);
    border: 1px solid rgba(15, 23, 42, 0.08);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    color: #0F172A;
    font-size: 11.5px;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .property-card-body {
    padding: 28px;
  }

  .price-header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
  }

  .prop-rent-display {
    font-family: var(--font-heading);
    font-size: 24px;
    font-weight: 800;
    color: #FF6B35;
  }

  .rent-period-label {
    font-size: 12px;
    font-weight: 600;
    color: #64748B;
  }

  .rent-deposit-badge {
    font-size: 11px;
    font-weight: 700;
    color: #64748B;
    background: rgba(15, 23, 42, 0.03);
    border: 1px solid rgba(15, 23, 42, 0.05);
    padding: 3px 8px;
    border-radius: 6px;
  }

  .property-card-title {
    font-family: var(--font-heading);
    font-size: 19px;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 8px;
    text-overflow: ellipsis;
    overflow: hidden;
    white-space: nowrap;
  }

  .property-card-address {
    font-size: 13.5px;
    color: #64748B;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 6px;
    font-weight: 500;
  }

  .pin-color {
    color: #FF6B35;
  }

  .spec-row {
    display: flex;
    gap: 16px;
    border-top: 1px solid rgba(15, 23, 42, 0.06);
    padding-top: 20px;
    font-size: 13px;
    color: #475569;
    margin-bottom: 24px;
    font-weight: 500;
  }

  .spec-item {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .spec-item i {
    font-size: 16px;
    color: #FF6B35;
  }

  .view-details-btn {
    width: 100%;
    background: rgba(15, 23, 42, 0.02);
    border: 1px solid rgba(15, 23, 42, 0.06);
    border-radius: 14px;
    color: #0f172a;
    font-size: 13.5px;
    font-weight: 600;
    padding: 14px;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .view-details-btn:hover {
    background: rgba(255, 107, 53, 0.06);
    border-color: rgba(255, 107, 53, 0.25);
    color: #FF6B35;
  }

  /* Testimonials Styling */
  .testimonials-section {
    padding: 120px 80px;
    background: #F8FAFC;
    border-top: 1px solid rgba(15, 23, 42, 0.04);
    position: relative;
    z-index: 5;
  }

  .testimonials-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
    gap: 32px;
    max-width: 1200px;
    margin: 0 auto;
  }

  .testimonial-card {
    background: #ffffff;
    border: 1px solid rgba(15, 23, 42, 0.05);
    border-radius: 24px;
    padding: 36px;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    transition: transform 0.3s;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.02);
  }
  .testimonial-card:hover {
    transform: translateY(-4px);
  }

  .testimonial-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }

  .testimonial-stars {
    color: #FFA800;
    font-size: 14px;
    display: flex;
    gap: 3px;
  }

  .quote-icon {
    font-size: 28px;
    color: rgba(255, 107, 53, 0.1);
  }

  .testimonial-quote {
    font-size: 15px;
    color: #475569;
    line-height: 1.65;
    font-style: italic;
    margin-bottom: 28px;
    font-weight: 500;
  }

  .testimonial-author {
    display: flex;
    align-items: center;
    gap: 14px;
  }

  .testimonial-avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    color: #fff;
    font-weight: 800;
    font-size: 14.5px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .avatar-orange {
    background: linear-gradient(135deg, #FF6B35 0%, #FFA800 100%);
  }

  .avatar-purple {
    background: linear-gradient(135deg, #7C3AED 0%, #A78BFA 100%);
  }

  .author-name {
    font-weight: 700;
    font-size: 14.5px;
    color: #0F172A;
  }

  .author-sub {
    font-size: 11.5px;
    color: #64748B;
    font-weight: 600;
    margin-top: 1px;
  }

  /* Gorgeous Call to Action Banner styling */
  .cta-banner-section {
    padding: 60px 80px 100px 80px;
    z-index: 5;
    position: relative;
    background: #ffffff;
  }

  .cta-card {
    max-width: 1200px;
    margin: 0 auto;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.98) 100%);
    border: 1px solid rgba(15, 23, 42, 0.06);
    border-radius: 32px;
    padding: 60px 40px;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 50px rgba(15, 23, 42, 0.05);
  }

  .cta-card-glow {
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255, 107, 53, 0.06) 0%, rgba(124, 58, 237, 0.02) 50%, rgba(0,0,0,0) 100%);
    pointer-events: none;
  }

  .cta-badge {
    font-size: 10.5px;
    font-weight: 800;
    color: #E85A24;
    background: rgba(255, 107, 53, 0.05);
    border: 1px solid rgba(255, 107, 53, 0.18);
    padding: 6px 14px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 1px;
    display: inline-block;
    margin-bottom: 24px;
  }

  .cta-card h3 {
    font-family: var(--font-heading);
    font-size: 36px;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 16px;
    letter-spacing: -0.8px;
  }

  .cta-card p {
    font-size: 16px;
    color: #475569;
    max-width: 600px;
    margin: 0 auto 36px auto;
    line-height: 1.6;
    font-weight: 500;
  }

  .cta-actions {
    display: flex;
    gap: 16px;
    justify-content: center;
    flex-wrap: wrap;
  }

  .cta-action-primary {
    background: linear-gradient(135deg, #FF6B35 0%, #FFA800 100%);
    border: none;
    color: white;
    font-weight: 700;
    border-radius: 30px;
    padding: 14px 36px;
    font-size: 15px;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(255, 107, 53, 0.3);
    transition: transform 0.2s, box-shadow 0.2s;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .cta-action-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(255, 107, 53, 0.4);
  }

  .cta-action-secondary {
    background: rgba(15, 23, 42, 0.02);
    border: 1px solid rgba(15, 23, 42, 0.08);
    color: #0F172A;
    font-weight: 600;
    border-radius: 30px;
    padding: 14px 32px;
    font-size: 15px;
    cursor: pointer;
    transition: background 0.2s;
  }
  .cta-action-secondary:hover {
    background: rgba(15, 23, 42, 0.06);
  }

  /* Ultra-clean Footer styling */
  .landing-footer {
    background: #F8FAFC;
    border-top: 1px solid rgba(15, 23, 42, 0.05);
    padding: 80px 80px 40px 80px;
    font-size: 14px;
    position: relative;
    z-index: 5;
  }

  .footer-container {
    max-width: 1200px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 2fr 1fr 1fr;
    gap: 60px;
    padding-bottom: 60px;
    border-bottom: 1px solid rgba(15, 23, 42, 0.06);
  }

  .footer-brand-desc {
    color: #64748B;
    max-width: 380px;
    line-height: 1.6;
    margin-bottom: 24px;
    font-weight: 500;
  }

  .footer-socials {
    display: flex;
    gap: 16px;
  }

  .footer-socials i {
    font-size: 20px;
    color: #94A3B8;
    cursor: pointer;
    transition: color 0.2s;
  }

  .footer-socials i:hover {
    color: #FF6B35;
  }

  .footer-links-column {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .footer-links-column h4 {
    font-size: 13.5px;
    font-weight: 800;
    color: #0F172A;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 16px;
  }

  .footer-link {
    color: #475569;
    font-weight: 500;
    cursor: pointer;
    transition: color 0.2s;
  }

  .footer-link:hover {
    color: #0F172A;
  }

  .footer-bottom {
    max-width: 1200px;
    margin: 0 auto;
    padding-top: 32px;
    display: flex;
    justify-content: space-between;
    color: #64748B;
    font-size: 12px;
    font-weight: 600;
    flex-wrap: wrap;
    gap: 16px;
  }

  /* Responsive breakpoints */
  @media (max-width: 992px) {
    .landing-header {
      padding: 16px 32px;
    }
    .hero-section {
      padding: 60px 32px;
    }
    .hero-grid-container {
      grid-template-columns: 1fr;
      text-align: center;
      gap: 40px;
    }
    .hero-text-block {
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .hero-desc {
      margin-left: auto;
      margin-right: auto;
    }
    .stats-row {
      justify-content: center;
    }
    .features-section, .public-properties-section, .testimonials-section, .cta-banner-section, .landing-footer {
      padding: 80px 32px;
    }
    .footer-container {
      grid-template-columns: 1fr;
      gap: 40px;
    }
  }

  @media (max-width: 600px) {
    .hero-text-block h1 {
      font-size: 40px;
      letter-spacing: -1px;
    }
    .search-widget-capsule {
      flex-direction: column;
      border-radius: 24px;
      padding: 16px;
      gap: 12px;
    }
    .widget-divider {
      width: 100%;
      height: 1px;
    }
    .search-action-btn {
      width: 100%;
    }
    .section-title {
      font-size: 28px;
    }
    .floating-mini-status-light {
      right: 0;
      bottom: -30px;
    }
    .glass-mockup-card-overlay {
      left: 10px;
      top: -30px;
    }
  }
</style>
