# components/navbar.py
import streamlit as st

def render_navbar():
    st.markdown("""
    <style>
        .navbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            width: 100%;
            height: 80px;
            background: #000000;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 3rem;
            z-index: 1000;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            border-bottom: 1px solid #333;
        }
        
        .navbar-brand {
            display: flex;
            align-items: center;
            font-size: 28px;
            font-weight: bold;
            text-decoration: none;
            color: white;
            font-family: 'Arial', sans-serif;
        }
        
        .logo-container {
            position: relative;
            width: 45px;
            height: 40px;
            margin-right: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        /* Shopping cart wireframe */
        .shopping-cart {
            position: absolute;
            width: 40px;
            height: 32px;
            top: 2px;
            left: 2px;
        }
        
        /* Cart main body - rectangular basket */
        .shopping-cart::before {
            content: '';
            position: absolute;
            bottom: 6px;
            left: 6px;
            width: 26px;
            height: 18px;
            border: 2px solid white;
            border-radius: 2px;
            background: transparent;
        }
        
        /* Cart handle - L-shaped towards right */
        .shopping-cart::after {
            content: '';
            position: absolute;
            top: 4px;
            right: 4px;
            width: 12px;
            height: 12px;
            border-top: 2px solid white;
            border-right: 2px solid white;
            background: transparent;
        }
        
        /* Cart wheels */
        .cart-wheels {
            position: absolute;
            bottom: 0;
            left: 12px;
            width: 5px;
            height: 5px;
            background: white;
            border-radius: 50%;
            box-shadow: 16px 0 0 white;
        }
        
        /* Camera lens - the main focal point */
        .camera-lens {
            position: absolute;
            width: 20px;
            height: 20px;
            background: #14b8a6;
            border-radius: 50%;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 2;
        }
        
        /* Outer lens ring */
        .camera-lens::before {
            content: '';
            width: 14px;
            height: 14px;
            background: transparent;
            border: 2px solid white;
            border-radius: 50%;
            position: absolute;
        }
        
        /* Inner lens center */
        .camera-lens::after {
            content: '';
            position: absolute;
            width: 6px;
            height: 6px;
            background: white;
            border-radius: 50%;
            z-index: 3;
        }
        
        .brand-text .pick-text {
            color: white;
        }
        
        .brand-text .pick-number {
            color: #14b8a6;
        }
        
        .navbar-nav {
            display: flex;
            list-style: none;
            margin: 0;
            padding: 0;
            gap: 2rem;
        }
        
        .navbar-nav li {
            margin: 0;
        }
        
        .navbar-nav a {
            color: white;
            text-decoration: none;
            font-size: 18px;
            font-weight: 500;
            padding: 10px 20px;
            border-radius: 6px;
            transition: all 0.3s ease;
            display: block;
            font-family: 'Arial', sans-serif;
        }
        
        .navbar-nav a:hover {
            background-color: rgba(20, 184, 166, 0.15);
            color: #14b8a6;
            transform: translateY(-2px);
        }
        
        /* Mobile menu toggle button */
        .mobile-menu-toggle {
            display: none;
            background: none;
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
            padding: 5px;
        }
        
        /* Responsive design */
        @media (max-width: 1024px) {
            .navbar {
                padding: 0 2rem;
            }
            
            .navbar-nav {
                gap: 1.5rem;
            }
        }
        
        @media (max-width: 768px) {
            .navbar {
                padding: 0 1rem;
                flex-wrap: wrap;
                height: auto;
                min-height: 80px;
            }
            
            .navbar-brand {
                font-size: 24px;
                flex: 1;
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
            }
            
            .navbar-nav.active {
                display: flex;
            }
            
            .navbar-nav a {
                font-size: 16px;
                padding: 12px 20px;
                border-bottom: 1px solid #333;
            }
            
            .navbar-nav a:hover {
                background-color: rgba(20, 184, 166, 0.15);
                transform: none;
            }
        }
        
        @media (max-width: 480px) {
            .navbar {
                padding: 0 0.75rem;
            }
            
            .navbar-brand {
                font-size: 20px;
            }
            
            .logo-container {
                margin-right: 10px;
            }
            
            .navbar-nav a {
                font-size: 14px;
                padding: 10px 15px;
            }
        }
        
        @media (max-width: 320px) {
            .navbar {
                padding: 0 0.5rem;
            }
            
            .navbar-brand {
                font-size: 18px;
            }
            
            .logo-container {
                margin-right: 8px;
            }
        }
        
        /* Add top margin to main content to account for fixed navbar */
        .main-content {
            margin-top: 80px;
        }
        
        @media (max-width: 768px) {
            .main-content {
                margin-top: 100px;
            }
        }
    </style>
    
    <div class="navbar">
        <div class="navbar-brand">
            <div class="logo-container">
                <div class="shopping-cart">
                    <div class="cart-wheels"></div>
                </div>
                <div class="camera-lens"></div>
            </div>
            <div class="brand-text">
                <span class="pic-text">Pic</span><span class="pick-number">2</span><span class="pick-text">Pick</span>
            </div>
        </div>
        <button class="mobile-menu-toggle" onclick="toggleMobileMenu()">☰</button>
        <ul class="navbar-nav" id="navbar-nav">
            <li><a href="/">Snap & Shop</a></li>
            <li><a href="#trends">Trends</a></li>
            <li><a href="#about">About</a></li>
            <li><a href="/contacts">Contacts</a></li>
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
        });
    </script>
    
    <!-- Add this div to your main content to account for fixed navbar -->
    <div class="main-content">
        <!-- Your main content goes here -->
    </div>
    """, unsafe_allow_html=True)