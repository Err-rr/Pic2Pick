# components/navbar.py
import streamlit as st

def render_navbar():
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        .navbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            width: 100%;
            height: 70px;
            background: #000000;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 2rem;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            border-bottom: 1px solid #222;
        }
        
        .navbar-brand {
            display: flex;
            align-items: center;
            font-size: 26px;
            font-weight: bold;
            text-decoration: none;
            color: white;
            font-family: 'Arial', sans-serif;
        }
        
        .title-icon {
            font-size: 28px;
            color: #14b8a6;
            margin-right: 12px;
        }
        
        .brand-text .pic-text {
            color: white;
        }
        
        .brand-text .pick-number {
            color: #14b8a6;
        }
        
        .brand-text .pick-text {
            color: white;
        }
        
        .navbar-nav {
            display: flex;
            list-style: none;
            margin: 0;
            padding: 0;
            gap: 1.5rem;
        }
        
        .navbar-nav li {
            margin: 0;
        }
        
        .navbar-nav a {
            color: white;
            text-decoration: none;
            font-size: 16px;
            font-weight: 500;
            padding: 8px 16px;
            border-radius: 8px;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
            font-family: 'Arial', sans-serif;
        }
        
        .navbar-nav a:hover {
            background-color: #14b8a6;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(20, 184, 166, 0.3);
        }
        
        .nav-icon {
            font-size: 16px;
            transition: transform 0.3s ease;
        }
        
        .navbar-nav a:hover .nav-icon {
            transform: scale(1.2);
        }
        
        /* Mobile menu toggle button */
        .mobile-menu-toggle {
            display: none;
            background: none;
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
            padding: 8px;
            border-radius: 4px;
            transition: background-color 0.3s ease;
        }
        
        .mobile-menu-toggle:hover {
            background-color: #333;
        }
        
        /* Responsive design */
        @media (max-width: 1024px) {
            .navbar {
                padding: 0 1.5rem;
            }
            
            .navbar-nav {
                gap: 1rem;
            }
        }
        
        @media (max-width: 768px) {
            .navbar {
                padding: 0 1rem;
                flex-wrap: wrap;
                height: auto;
                min-height: 70px;
            }
            
            .navbar-brand {
                font-size: 22px;
                flex: 1;
            }
            
            .title-icon {
                font-size: 24px;
                margin-right: 10px;
            }
            
            .mobile-menu-toggle {
                display: block;
                order: 2;
            }
            
            .navbar-nav {
                display: none;
                width: 100%;
                flex-direction: column;
                gap: 0;
                margin-top: 1rem;
                padding-bottom: 1rem;
                order: 3;
                background: #000;
            }
            
            .navbar-nav.active {
                display: flex;
            }
            
            .navbar-nav a {
                font-size: 15px;
                padding: 12px 16px;
                border-bottom: 1px solid #333;
                border-radius: 0;
            }
            
            .navbar-nav a:hover {
                background-color: #14b8a6;
                transform: none;
                border-radius: 0;
            }
        }
        
        @media (max-width: 480px) {
            .navbar {
                padding: 0 0.75rem;
            }
            
            .navbar-brand {
                font-size: 20px;
            }
            
            .title-icon {
                font-size: 22px;
                margin-right: 8px;
            }
            
            .navbar-nav a {
                font-size: 14px;
                padding: 10px 12px;
            }
        }
        
        /* Add top margin to main content to account for fixed navbar */
        .main-content {
            margin-top: 70px;
        }
        
        @media (max-width: 768px) {
            .main-content {
                margin-top: 90px;
            }
        }
        
        /* Smooth scrolling for anchor links */
        html {
            scroll-behavior: smooth;
        }
    </style>
    
    <div class="navbar">
        <div class="navbar-brand">
            <i class="fas fa-shopping-bag title-icon icon"></i>
            <div class="brand-text">
                <span class="pic-text">Pic</span><span class="pick-number">2</span><span class="pick-text">Pick</span>
            </div>
        </div>
        <button class="mobile-menu-toggle" onclick="toggleMobileMenu()">
            <i class="fas fa-bars"></i>
        </button>
        <ul class="navbar-nav" id="navbar-nav">
            <li>
                <a href="/">
                    <i class="fas fa-camera nav-icon"></i>
                    <span>Snap & Shop</span>
                </a>
            </li>
            <li>
                <a href="#trends">
                    <i class="fas fa-fire nav-icon"></i>
                    <span>Trends</span>
                </a>
            </li>
            <li>
                <a href="#about">
                    <i class="fas fa-info-circle nav-icon"></i>
                    <span>About</span>
                </a>
            </li>
            <li>
                <a href="/contacts">
                    <i class="fas fa-envelope nav-icon"></i>
                    <span>Contacts</span>
                </a>
            </li>
        </ul>
    </div>
    
    <script>
        function toggleMobileMenu() {
            const navMenu = document.getElementById('navbar-nav');
            navMenu.classList.toggle('active');
        }
        
        // Close mobile menu when clicking on a link
        document.addEventListener('DOMContentLoaded', function() {
            const navLinks = document.querySelectorAll('.navbar-nav a');
            navLinks.forEach(link => {
                link.addEventListener('click', function() {
                    const navMenu = document.getElementById('navbar-nav');
                    navMenu.classList.remove('active');
                });
            });
            
            // Close mobile menu when clicking outside
            document.addEventListener('click', function(event) {
                const navbar = document.querySelector('.navbar');
                const navMenu = document.getElementById('navbar-nav');
                const toggleButton = document.querySelector('.mobile-menu-toggle');
                
                if (!navbar.contains(event.target) && navMenu.classList.contains('active')) {
                    navMenu.classList.remove('active');
                }
            });
        });
    </script>
    
    <!-- Add this div to your main content to account for fixed navbar -->
    <div class="main-content">
        <!-- Your main content goes here -->
    </div>
    """, unsafe_allow_html=True)