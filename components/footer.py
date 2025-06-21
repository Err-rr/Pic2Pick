# components/footer.py
import streamlit as st

def render_footer():
    st.markdown("""
    <style>
        /* Reset Streamlit's default margins and padding */
        .main > div {
            padding-bottom: 0 !important;
        }
        
        .block-container {
            padding-bottom: 0 !important;
        }
        
        /* Footer positioning and styling */
        .custom-footer {
            background: #000000 !important;
            color: white;
            width: calc(100vw - 17px);
            position: relative;
            left: calc(-50vw + 50% + 8.5px);
            margin-left: 0 !important;
            margin-right: 0 !important;
            margin-top: 4rem;
            padding: 3rem 0;
            box-sizing: border-box;
            border-top: 1px solid #333;
        }
        
        .footer-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
            display: flex;
            flex-direction: column;
            gap: 2rem;
            align-items: center;
            width: 100%;
            box-sizing: border-box;
        }
        
        .footer-nav {
            display: flex;
            justify-content: center;
            gap: 2.5rem;
            flex-wrap: wrap;
            margin-bottom: 1rem;
            width: 100%;
        }
        
        .footer-nav a {
            color: white;
            text-decoration: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            transition: all 0.3s ease;
            font-weight: 500;
            font-size: 1rem;
            border: 2px solid transparent;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            cursor: pointer;
        }
        
        .footer-nav a:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.2);
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        }
        
        .footer-divider {
            width: 100%;
            max-width: 600px;
            height: 1px;
            background: linear-gradient(90deg, transparent, #333, transparent);
            margin: 1rem 0;
        }
        
        .footer-info {
            text-align: center;
            width: 100%;
        }
        
        .footer-info .copyright {
            margin: 0 0 0.5rem 0;
            font-size: 0.95rem;
            opacity: 0.8;
            font-weight: 400;
        }
        
        .footer-info .made-by {
            font-size: 0.9rem;
            opacity: 0.7;
            font-weight: 300;
            letter-spacing: 0.5px;
        }
        
        .footer-info .heart {
            color: #ff6b6b;
            animation: heartbeat 2s ease-in-out infinite;
            display: inline-block;
        }
        
        @keyframes heartbeat {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .custom-footer {
                padding: 2.5rem 0;
                margin-top: 3rem;
            }
            
            .footer-container {
                padding: 0 1.5rem;
                gap: 1.5rem;
            }
            
            .footer-nav {
                gap: 1.5rem;
                flex-direction: column;
                align-items: center;
            }
            
            .footer-nav a {
                padding: 0.8rem 2rem;
                min-width: 150px;
                text-align: center;
                font-size: 0.95rem;
            }
        }
        
        @media (max-width: 480px) {
            .custom-footer {
                padding: 2rem 0;
                margin-top: 2rem;
            }
            
            .footer-container {
                padding: 0 1rem;
            }
            
            .footer-nav a {
                font-size: 0.9rem;
                padding: 0.7rem 1.5rem;
                min-width: 130px;
            }
            
            .footer-info .copyright {
                font-size: 0.85rem;
            }
            
            .footer-info .made-by {
                font-size: 0.8rem;
            }
        }
        
        /* Ensure full width coverage at all screen sizes */
        @media (min-width: 1px) {
            .custom-footer {
                width: calc(100vw - 17px) !important;
                left: calc(-50vw + 50% + 8.5px) !important;
                background: #000000 !important;
            }
        }
        
        /* Additional overrides to ensure solid black background */
        .custom-footer::before,
        .custom-footer::after {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Use st.html for better control over the footer placement
    st.html("""
    <div class="custom-footer" id="customFooter">
        <div class="footer-container">
            <div class="footer-nav">
                <a href="#trends" onclick="handleNavClick('trends')">Check Trends</a>
                <a href="#bug-report" onclick="handleNavClick('bug-report')">Report Bug</a>
                <a href="#contact" onclick="handleNavClick('contact')">Contact</a>
            </div>
            <div class="footer-divider"></div>
            <div class="footer-info">
                <div class="copyright">&copy; 2025 Pic2Pick. All rights reserved.</div>
                <div class="made-by">
                    Made with <span class="heart">❤️</span> by Shivam
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function handleNavClick(section) {
            // Add your navigation logic here
            console.log('Navigating to:', section);
            // Example: window.location.hash = section;
        }
        
        // Dynamically adjust footer width to account for scrollbar
        function adjustFooterWidth() {
            const footer = document.getElementById('customFooter');
            const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
            const adjustedWidth = `calc(100vw - ${scrollbarWidth}px)`;
            const adjustedLeft = `calc(-50vw + 50% + ${scrollbarWidth/2}px)`;
            
            footer.style.width = adjustedWidth;
            footer.style.left = adjustedLeft;
        }
        
        // Adjust on load and resize
        window.addEventListener('load', adjustFooterWidth);
        window.addEventListener('resize', adjustFooterWidth);
        
        // Run immediately
        adjustFooterWidth();
    </script>
    """)