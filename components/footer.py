# components/footer.py
import streamlit as st

def render_footer():
    st.markdown("""
    <style>
        .footer {
            background: #000000;
            color: white;
            padding: 2rem 1rem;
            margin-top: 3rem;
            text-align: center;
            position: relative;
            width: 100vw;
            margin-left: calc(-50vw + 50%);
            box-sizing: border-box;
            clear: both;
        }
        
        .footer-content {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }
        
        .footer-links {
            display: flex;
            justify-content: center;
            gap: 2rem;
            flex-wrap: wrap;
        }
        
        .footer-links a {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: background-color 0.3s ease, transform 0.2s ease;
            font-weight: 500;
        }
        
        .footer-links a:hover {
            background-color: #333333;
            transform: translateY(-2px);
        }
        
        .footer-bottom {
            border-top: 1px solid #333333;
            padding-top: 1rem;
            margin-top: 1rem;
        }
        
        .footer-bottom p {
            margin: 0;
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        .made-with-love {
            font-size: 0.85rem;
            margin-top: 0.5rem;
            opacity: 0.7;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .footer {
                padding: 1.5rem 1rem;
            }
            
            .footer-links {
                gap: 1rem;
                flex-direction: column;
                align-items: center;
            }
            
            .footer-links a {
                padding: 0.75rem 1.5rem;
                min-width: 120px;
            }
        }
        
        @media (max-width: 480px) {
            .footer {
                padding: 1rem 0.5rem;
            }
            
            .footer-links a {
                font-size: 0.9rem;
                padding: 0.6rem 1rem;
            }
            
            .footer-bottom p {
                font-size: 0.8rem;
            }
            
            .made-with-love {
                font-size: 0.75rem;
            }
        }
    </style>
    
    <div class="footer">
        <div class="footer-content">
            <div class="footer-links">
                <a href="#trends">Check Trends</a>
                <a href="#bug-report">Report Bug</a>
                <a href="#contact">Contact</a>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2025 Pic2Pick. All rights reserved.</p>
                <div class="made-with-love">Made with ❤️ by Shivam</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)