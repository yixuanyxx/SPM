<template>
    <div class="app-layout ms-2">
      <!-- Side Navigation -->
      <SideNavbar />
      
      <!-- Main Content Area -->
      <div class="app-container">
        <!-- Header Section -->
        <div class="header-section">
          <div class="header-content">
            <h1 class="page-title">My Projects</h1>
            <p class="page-subtitle">View and manage your project collaborations</p>
          </div>
        </div>
  
        <!-- Main Content -->
        <div class="main-content">
          <div class="projects-grid">
            <!-- Project Card 1 -->
            <div class="project-card" @click="handleCardClick">
              <div class="project-header">
                <h3 class="project-title">Q4 Marketing Campaign</h3>
                <p class="project-description">
                  Complete overhaul of marketing strategy for the fourth quarter, including social media campaigns, email marketing, and content creation.
                </p>
              </div>
  
              <div class="project-meta">
                <div class="meta-item">
                  <div class="meta-icon">
                    <i class="bi bi-person"></i>
                  </div>
                  <span>Manager: <span class="owner-name">Sarah Johnson</span></span>
                </div>
                <div class="meta-item">
                  <div class="meta-icon">
                    <i class="bi bi-people"></i>
                  </div>
                  <span>Collaborators:</span>
                  <div class="collaborators">
                    <div class="avatar">AK</div>
                    <div class="avatar">MR</div>
                    <div class="avatar">JD</div>
                    <div class="avatar more-collaborators">+2</div>
                  </div>
                </div>
              </div>
  
              <div class="progress-section">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: '60%' }"></div>
                </div>
                <div class="progress-text">3 of 5 tasks completed</div>
              </div>
  
              <div class="my-tasks">
                <div class="tasks-header">
                  <span class="tasks-title">My Tasks (2)</span>
                  <button class="expand-btn" @click.stop="toggleTasks($event)">
                    View All
                  </button>
                </div>
                
                <div class="my-tasks-list">
                  <div class="task-item">
                    <span class="task-name">Create social media content</span>
                    <span class="task-date">Oct 15</span>
                  </div>
                  <div class="task-item">
                    <span class="task-name">Review campaign metrics</span>
                    <span class="task-date">Oct 20</span>
                  </div>
                </div>
  
                <div class="all-tasks">
                  <div class="task-item">
                    <div class="task-content">
                      <span class="task-name">Design email templates</span>
                      <span class="task-assignee">(Maria)</span>
                    </div>
                    <span class="status-badge status-completed">Completed</span>
                  </div>
                  <div class="task-item">
                    <div class="task-content">
                      <span class="task-name">Set up analytics tracking</span>
                      <span class="task-assignee">(John)</span>
                    </div>
                    <span class="status-badge status-review">Review</span>
                  </div>
                  <div class="task-item">
                    <div class="task-content">
                      <span class="task-name">Content calendar planning</span>
                      <span class="task-assignee">(Alex)</span>
                    </div>
                    <span class="status-badge status-ongoing">Ongoing</span>
                  </div>
                </div>
              </div>
            </div>
  
            <!-- Project Card 2 -->
            <div class="project-card" @click="handleCardClick">
              <div class="project-header">
                <h3 class="project-title">Website Redesign</h3>
                <p class="project-description">
                  Modern redesign of the company website with improved user experience, mobile responsiveness, and updated branding.
                </p>
              </div>
  
              <div class="project-meta">
                <div class="meta-item">
                  <div class="meta-icon">
                    <i class="bi bi-person"></i>
                  </div>
                  <span>Manager: <span class="owner-name">David Chen</span></span>
                </div>
                <div class="meta-item">
                  <div class="meta-icon">
                    <i class="bi bi-people"></i>
                  </div>
                  <span>Collaborators:</span>
                  <div class="collaborators">
                    <div class="avatar">LC</div>
                    <div class="avatar">TP</div>
                    <div class="avatar">RW</div>
                  </div>
                </div>
              </div>
  
              <div class="progress-section">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: '25%' }"></div>
                </div>
                <div class="progress-text">1 of 4 tasks completed</div>
              </div>
  
              <div class="my-tasks">
                <div class="tasks-header">
                  <span class="tasks-title">My Tasks (1)</span>
                  <button class="expand-btn" @click.stop="toggleTasks($event)">
                    View All
                  </button>
                </div>
                
                <div class="my-tasks-list">
                  <div class="task-item">
                    <span class="task-name">User research analysis</span>
                    <span class="task-date">Oct 25</span>
                  </div>
                </div>
  
                <div class="all-tasks">
                  <div class="task-item">
                    <div class="task-content">
                      <span class="task-name">Wireframe creation</span>
                      <span class="task-assignee">(Lisa)</span>
                    </div>
                    <span class="status-badge status-ongoing">Ongoing</span>
                  </div>
                  <div class="task-item">
                    <div class="task-content">
                      <span class="task-name">Brand guidelines review</span>
                      <span class="task-assignee">(Tom)</span>
                    </div>
                    <span class="status-badge status-completed">Completed</span>
                  </div>
                  <div class="task-item">
                    <div class="task-content">
                      <span class="task-name">Technical requirements</span>
                      <span class="task-assignee">(Rachel)</span>
                    </div>
                    <span class="status-badge status-review">Review</span>
                  </div>
                </div>
              </div>
            </div>
  
            <!-- Project Card 3 -->
            <div class="project-card" @click="handleCardClick">
              <div class="project-header">
                <h3 class="project-title">Product Launch Beta</h3>
                <p class="project-description">
                  Coordinate the beta testing phase for our new product launch, including user feedback collection and bug fixes.
                </p>
              </div>
  
              <div class="project-meta">
                <div class="meta-item">
                  <div class="meta-icon">
                    <i class="bi bi-person"></i>
                  </div>
                  <span>Manager: <span class="owner-name">Emily Rodriguez</span></span>
                </div>
                <div class="meta-item">
                  <div class="meta-icon">
                    <i class="bi bi-people"></i>
                  </div>
                  <span>Collaborators:</span>
                  <div class="collaborators">
                    <div class="avatar">KS</div>
                    <div class="avatar">BL</div>
                  </div>
                </div>
              </div>
  
              <div class="progress-section">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: '80%' }"></div>
                </div>
                <div class="progress-text">4 of 5 tasks completed</div>
              </div>
  
              <div class="my-tasks">
                <div class="tasks-header">
                  <span class="tasks-title">My Tasks (3)</span>
                  <button class="expand-btn" @click.stop="toggleTasks($event)">
                    View All
                  </button>
                </div>
                
                <div class="my-tasks-list">
                  <div class="task-item">
                    <span class="task-name">Beta user recruitment</span>
                    <span class="task-date">Completed</span>
                  </div>
                  <div class="task-item">
                    <span class="task-name">Feedback analysis report</span>
                    <span class="task-date">Oct 18</span>
                  </div>
                  <div class="task-item">
                    <span class="task-name">Launch timeline review</span>
                    <span class="task-date">Oct 22</span>
                  </div>
                </div>
  
                <div class="all-tasks">
                  <div class="task-item">
                    <div class="task-content">
                      <span class="task-name">Bug tracking setup</span>
                      <span class="task-assignee">(Kevin)</span>
                    </div>
                    <span class="status-badge status-completed">Completed</span>
                  </div>
                  <div class="task-item">
                    <div class="task-content">
                      <span class="task-name">Testing documentation</span>
                      <span class="task-assignee">(Beth)</span>
                    </div>
                    <span class="status-badge status-completed">Completed</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
    import SideNavbar from '../../components/SideNavbar.vue'
    import '../projectview/projectview.css'

  
  // Methods
  const toggleTasks = (event) => {
    const button = event.target
    const projectCard = button.closest('.project-card')
    const allTasks = projectCard.querySelector('.all-tasks')
    const isExpanded = allTasks.classList.contains('expanded')
    
    if (isExpanded) {
      allTasks.classList.remove('expanded')
      button.textContent = 'View All'
    } else {
      allTasks.classList.add('expanded')
      button.textContent = 'Show Less'
    }
  }
  
  const handleCardClick = (event) => {
    // Don't trigger if clicking on buttons
    if (event.target.classList.contains('expand-btn')) return
    
    // Add a subtle animation effect
    const card = event.currentTarget
    card.style.transform = 'scale(1.02)'
    setTimeout(() => {
      card.style.transform = 'scale(1)'
    }, 150)
  }
  </script>
  
 