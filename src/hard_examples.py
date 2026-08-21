HARD_EXAMPLES = [
    # ══════════════════════════════════════════════════════════════════════
    #  HARD NEGATIVES — Genuine jobs with surface-level suspicious keywords
    # ══════════════════════════════════════════════════════════════════════
    {
        'title': 'Remote Graphic Design Intern',
        'company_profile': 'PixelCraft Studios is a boutique remote-first design agency in Bengaluru.',
        'description': 'We are looking for a remote Graphic Design Intern. This is a Work From Home opportunity with a stipend of Rs 15,000 per month. Requirements: Figma, Photoshop, Illustrator. Flexible hours, dynamic startup culture.',
        'requirements': 'Bachelor in Design or Fine Arts. Portfolio required. To apply, submit your Behance link or email careers@pixelcraft.in.',
        'fraudulent': 0,
        'source': 'hard_examples'
    },
    {
        'title': 'Content Writer (Part Time / WFH)',
        'company_profile': 'TechDigest Media',
        'description': 'Urgently hiring part-time content writers for tech news articles. Earn Rs 20,000 pm working 15 hours a week. WFH flexible shifts.',
        'requirements': 'Excellent English grammar, knowledge of SEO. Email your sample articles to hr@techdigestmedia.com.',
        'fraudulent': 0,
        'source': 'hard_examples'
    },
    {
        'title': 'Junior Python Developer',
        'company_profile': 'NovaSoft Systems',
        'description': 'Immediate hiring for Python developers. Immediate joining preferred. Salary: 4.5 LPA - 6 LPA. Spot interview slots available for qualified candidates.',
        'requirements': 'Django/Flask experience, basic SQL. Apply via company careers portal at https://novasoft.com/careers.',
        'fraudulent': 0,
        'source': 'hard_examples'
    },
    {
        'title': 'Customer Support Representative',
        'company_profile': 'Connect360 Services',
        'description': 'Walk-in interview this week! Immediate selection based on communication skills round. Salary Rs 18,000/month.',
        'requirements': 'HSC or Graduate. Good verbal English skills. Location: Cyber City Gurgaon. Official email: recruitment@connect360.co.in.',
        'fraudulent': 0,
        'source': 'hard_examples'
    },
    {
        'title': 'Data Entry & Administrative Assistant',
        'company_profile': 'Apex Logistics India Pvt Ltd',
        'description': 'We need a data entry clerk for cataloging shipment invoices. Fixed salary Rs 22,000 pm. Working hours 9 AM to 5 PM.',
        'requirements': 'MS Excel proficiency, typing speed 35 wpm. No prior corporate experience needed. Apply at https://apexlogistics.in/jobs.',
        'fraudulent': 0,
        'source': 'hard_examples'
    },
    {
        'title': 'Marketing Associate (Work From Home)',
        'company_profile': 'GreenRoots E-commerce Startup',
        'description': 'Join a fast growing eco-friendly brand. Remote work option available. Stipend: Rs 12,000/month plus performance bonus.',
        'requirements': 'Social media management, Canva. Send CV to hr@greenroots.co.',
        'fraudulent': 0,
        'source': 'hard_examples'
    },
    {
        'title': 'Urgent Requirement: QA Software Tester',
        'company_profile': 'Syntellect Technologies',
        'description': 'Urgent hiring for manual test engineer. Immediate joining required. Good pay as per market standards.',
        'requirements': 'Selenium, Postman, Bugzilla. Email resume to jobs@syntellect.com.',
        'fraudulent': 0,
        'source': 'hard_examples'
    },
    {
        'title': 'Operations Coordinator',
        'company_profile': 'Vanguard Supply Chain Solutions',
        'description': 'Managing daily warehouse dispatches and logistics documentation. Stipend Rs 16,000 per month.',
        'requirements': 'Graduate in any discipline. Apply directly on our official website https://vanguardlogistics.com.',
        'fraudulent': 0,
        'source': 'hard_examples'
    },
    # -- New hard negatives: genuine postings that look suspicious --
    {
        'title': 'Freelance Video Editor (Remote)',
        'company_profile': 'Reel Motion Studios is a video production company based in Mumbai, registered under MCA since 2018.',
        'description': 'Hiring freelance video editors on project basis. Payment per video: Rs 3,000 - Rs 8,000 depending on complexity. Work from home. Immediate openings. Quick turnaround projects for YouTube creators.',
        'requirements': 'Proficiency in Premiere Pro and After Effects. Portfolio link mandatory. Apply at https://reelmotion.in/apply.',
        'fraudulent': 0,
        'source': 'hard_examples'
    },
    {
        'title': 'Campus Ambassador - Tech Startup',
        'company_profile': 'CodeBridge Education Pvt Ltd (GST: 29AACC1234B1Z5)',
        'description': 'Looking for energetic campus ambassadors. Earn Rs 5,000/month stipend + Rs 500 per referral who registers for our coding bootcamp. Not an MLM - this is a marketing role with fixed stipend.',
        'requirements': 'Currently enrolled in B.Tech/BCA/MCA. Must have social media presence. Apply at https://codebridge.edu.in/ambassador.',
        'fraudulent': 0,
        'source': 'hard_examples'
    },
    {
        'title': 'Sales Executive - Insurance (Walk-in)',
        'company_profile': 'HDFC Life Insurance Company Limited',
        'description': 'Walk-in drive for sales executive position. Selected candidates get immediate joining. Salary: Rs 25,000 fixed + incentives. No prior experience required. Training provided.',
        'requirements': 'Graduate in any discipline. Carry your resume, 2 passport photos, Aadhaar copy for document verification at interview. Venue: HDFC Life Office, Cyber Hub, Gurgaon.',
        'fraudulent': 0,
        'source': 'hard_examples'
    },
    {
        'title': 'Backend Developer Intern',
        'company_profile': 'BuildStack Technologies',
        'description': 'We are a Y Combinator backed startup looking for backend interns. Stipend Rs 25,000/month. Remote first. Immediate joining for candidates who can start within a week.',
        'requirements': 'Node.js, PostgreSQL, Docker basics. GitHub profile required. Apply at careers@buildstack.io.',
        'fraudulent': 0,
        'source': 'hard_examples'
    },
    {
        'title': 'Telecaller - Loan Processing',
        'company_profile': 'Bajaj Finserv Direct',
        'description': 'Hiring telecallers for personal loan and credit card lead generation. Fixed salary Rs 15,000 + Rs 200 per conversion. Work from office, Andheri East, Mumbai.',
        'requirements': 'HSC pass. Good Hindi and English communication. Carry original Aadhaar and PAN for BGV at joining.',
        'fraudulent': 0,
        'source': 'hard_examples'
    },
    {
        'title': 'Technical Writer (Contract)',
        'company_profile': 'Documint Solutions - A registered MSME documentation services company.',
        'description': 'Looking for technical writers for API documentation project. Payment: Rs 2.5 per word, minimum 5000 words per week guaranteed. WhatsApp group for project coordination only - all payments via bank NEFT.',
        'requirements': 'Experience with Swagger/OpenAPI. Samples required. Email resume to hiring@documint.co.in.',
        'fraudulent': 0,
        'source': 'hard_examples'
    },
    {
        'title': 'Delivery Partner - Immediate Joining',
        'company_profile': 'Swiggy',
        'description': 'Earn Rs 18,000 - Rs 30,000 per month as a Swiggy delivery partner. No interview required - direct onboarding after document verification. Flexible hours, daily payouts available.',
        'requirements': 'Valid driving license, own two-wheeler. Download Swiggy delivery partner app from Play Store to register.',
        'fraudulent': 0,
        'source': 'hard_examples'
    },
    {
        'title': 'Human Resources Intern',
        'company_profile': 'TalentPulse HR Consulting, Bengaluru. Established 2015.',
        'description': 'HR internship with stipend Rs 10,000/month. Work from home with weekly office visits. Certificate provided. Immediate joining available.',
        'requirements': 'MBA HR student or graduate. Knowledge of recruitment platforms. Apply via Internshala or email hr@talentpulse.in.',
        'fraudulent': 0,
        'source': 'hard_examples'
    },

    # ══════════════════════════════════════════════════════════════════════
    #  HARD POSITIVES — Professional-sounding scams with subtle red flags
    # ══════════════════════════════════════════════════════════════════════
    {
        'title': 'Senior Executive - Enterprise Solutions',
        'company_profile': 'Global Tech Consulting Group (GTCG) is a premier technology advisory firm operating across APAC.',
        'description': 'We are expanding our enterprise architecture division and seeking qualified professionals. Selected candidates will undergo a mandatory 3-week specialized cloud security certification training module prior to project allocation. A refundable training gate fee deposit of Rs 2,499 is payable via UPI upon selection to confirm seat reservation.',
        'requirements': 'B.Tech/BE in Computer Science or IT. Minimum 1 year experience. Send CV and payment confirmation receipt to gtcg-careers@gmail.com.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },
    {
        'title': 'Associate Project Manager',
        'company_profile': 'Horizon Innovations International',
        'description': 'Horizon Innovations is hiring Associate Project Managers for corporate client implementations. Direct selection based on resume screening without interview rounds due to urgent project timeline constraints.',
        'requirements': 'PMP certification preferred. Candidates must submit ID proof and transfer refundable onboarding registration fee of Rs 1,850 to official HR UPI account.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },
    {
        'title': 'Data Analytics Specialist',
        'company_profile': 'Acuity Research & Insights',
        'description': 'Earn Rs 85,000 per month doing data validation and form processing work from home. High salary package offered for entry level background. Spot offer letter issued instantly.',
        'requirements': 'Laptop and smartphone required. Security deposit for company laptop allocation Rs 3,500 via PhonePe.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },
    {
        'title': 'Human Resources Manager',
        'company_profile': 'Pinnacle Talent Partners',
        'description': 'Looking for an experienced HR Manager to handle pan-India recruitment operations. Remuneration Rs 70,000/pm. Work from home.',
        'requirements': 'Applicants must transfer background verification processing charge Rs 1,200 to WhatsApp contact +91 9812345678.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },
    {
        'title': 'Software Development Engineer in Test (SDET)',
        'company_profile': 'Infosys Careers Recruitment Partner',
        'description': 'Off-campus recruitment drive for SDET role at Infosys client location. Direct joining letter issued upon document submission.',
        'requirements': 'Java, TestNG, Cucumber. Candidates must pay gate pass processing fee Rs 2,000 on http://infosys-careers-portal.com.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },
    {
        'title': 'Digital Marketing Strategist',
        'company_profile': 'Vanguard Media House',
        'description': 'We are hiring a Digital Marketing Strategist. High salary package of Rs 95,000 per month for freshers. Immediate joining within 24 hours.',
        'requirements': 'SEO, Google Ads, Meta Ads. Send Aadhaar card, PAN card, and bank passbook copy via WhatsApp for instant joining.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },
    {
        'title': 'Financial Analyst',
        'company_profile': 'Meridian Capital Advisory',
        'description': 'Meridian Capital is seeking a Junior Financial Analyst. Selected candidate will manage equity research sheets. No interview required.',
        'requirements': 'B.Com/MBA. Security deposit for corporate laptop Rs 4,999 to be remitted before onboarding.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },
    {
        'title': 'Corporate Communications Executive',
        'company_profile': 'Apex Global Relations',
        'description': 'Drafting press releases and managing public relations. Salary: Rs 60,000 pm WFH. Urgent requirement apply within 6 hours.',
        'requirements': 'Mass Communication degree. Email your profile and registration processing fee receipt to apexglobal@yahoo.com.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },

    # -- New: Telegram/WhatsApp group scams --
    {
        'title': 'Online Part Time Task Worker',
        'company_profile': 'SmartEarn Digital',
        'description': 'Join our Telegram channel @SmartEarnTasks for daily tasks. Complete simple tasks like liking videos, rating apps, and writing reviews. Earn Rs 3,000 - Rs 8,000 per day easily from your mobile phone. No experience needed. Daily payment to your bank account.',
        'requirements': 'Smartphone with internet connection. Join Telegram channel and contact admin for activation fee of Rs 299. WhatsApp: +91 8765432109.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },
    {
        'title': 'Social Media Evaluator',
        'company_profile': 'ClickRewards International',
        'description': 'Work from home opportunity. Simple tasks - rate products, review apps on Play Store, like Instagram posts. Get paid Rs 50-200 per task. Average daily earnings Rs 5,000. Thousands of people are already earning. Join our WhatsApp group for task allocation.',
        'requirements': 'No skills required. Activate your account by paying one-time registration of Rs 499 via GPay to our coordinator. WhatsApp +91 7654321098 for group link.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },
    {
        'title': 'YouTube Video Liker / Subscriber Job',
        'company_profile': 'DigiTask Solutions',
        'description': 'Earn money by watching YouTube videos and subscribing to channels. Rs 25 per video watched. Minimum 100 videos per day. Daily income Rs 2,500 guaranteed. Payment via UPI every evening. Join Telegram @DigiTaskJobs.',
        'requirements': 'Gmail account and YouTube account needed. Registration fee Rs 199 to start receiving tasks. Contact on Telegram for payment details.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },

    # -- New: LinkedIn impersonation scams --
    {
        'title': 'Business Analyst - TCS Digital',
        'company_profile': 'TCS Recruitment Cell (Official Partner)',
        'description': 'TCS is conducting an off-campus hiring drive for Business Analysts. Selected candidates will be placed in TCS Digital vertical. CTC: 7-12 LPA. This is a special drive not listed on TCS careers website. Direct offer letter within 48 hours of application.',
        'requirements': 'B.E./B.Tech with 60% aggregate. Process your application by paying Rs 1,500 examination fee at http://tcs-offcampus-drive.in. Send payment screenshot to tcsrecruitment2024@gmail.com.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },
    {
        'title': 'Associate Consultant - Deloitte India',
        'company_profile': 'Deloitte USI Hiring Partner',
        'description': 'Deloitte India is hiring Associate Consultants through referral partner channel. This vacancy is not publicly advertised. Walk-in selection at our partner office. Salary: 8-15 LPA depending on experience.',
        'requirements': 'MBA/CA/CFA preferred. Carry your resume, education certificates, and verification processing charges of Rs 2,200 (refundable after joining). Contact HR WhatsApp: +91 9988776655.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },
    {
        'title': 'Cloud Engineer - Amazon AWS Team',
        'company_profile': 'Amazon India Staffing Solutions',
        'description': 'Amazon Web Services team in Hyderabad is looking for Cloud Engineers. Package: 18-25 LPA. This is a backdoor referral entry not available on amazon.jobs. Guaranteed placement after clearing online aptitude test.',
        'requirements': 'AWS certification preferred. Pay test registration fee of Rs 3,000 at http://amazon-aws-hiring.com. Results within 24 hours. No interview needed for selected candidates.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },

    # -- New: MLM / pyramid scheme disguised as jobs --
    {
        'title': 'Business Development Partner',
        'company_profile': 'WealthNest Financial Group',
        'description': 'Become an independent business partner. Earn Rs 50,000 - Rs 2,00,000 per month. Build your own team of associates. Earn 15% commission on every team member enrollment. Unlimited income potential. Work your own hours.',
        'requirements': 'No qualification needed. Invest Rs 5,000 starter kit fee to activate your business partner account. Refer 5 people to recover your investment. Contact: wealthnest.partner@gmail.com.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },
    {
        'title': 'Independent Sales Consultant',
        'company_profile': 'LifeVantage Wellness India',
        'description': 'Join the wellness revolution. Sell premium health supplements. No boss, no fixed hours. Earn through direct sales plus team building bonuses. Top earners make Rs 5 lakhs per month. Free training webinars. Attend our success seminar this Saturday.',
        'requirements': 'Purchase starter product kit worth Rs 8,500 to begin. Earn commission on every product sold and every new consultant you recruit under your network.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },
    {
        'title': 'Affiliate Marketing Manager',
        'company_profile': 'CashFlow Network International',
        'description': 'Earn passive income by building your referral network. Rs 1,000 per referral signup. Unlimited referrals allowed. Top referrers earn Rs 1,00,000+ monthly. This is not a regular job - this is a business opportunity.',
        'requirements': 'Activation fee Rs 2,999 to join the affiliate network. Each person you refer pays the same fee and you earn from their referrals too. Multi-tier commission structure.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },

    # -- New: Crypto / trading scams disguised as jobs --
    {
        'title': 'Cryptocurrency Trading Analyst',
        'company_profile': 'CryptoEdge Capital',
        'description': 'Earn Rs 10,000 per day as a crypto trading analyst. We provide signals, you place trades. Guaranteed returns of 15-30% monthly. No prior trading experience needed. Our AI bot handles all analysis.',
        'requirements': 'Minimum investment of Rs 15,000 to start trading. Open account on our platform at http://cryptoedge-trade.com. Profits withdrawable daily.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },
    {
        'title': 'Forex Market Research Intern',
        'company_profile': 'GlobalFX Academy & Trading',
        'description': 'Learn forex trading while earning. Stipend Rs 20,000/month plus trading profits. Our proprietary algorithm generates consistent daily returns. Selected interns get access to our VIP Telegram signals channel.',
        'requirements': 'Deposit Rs 10,000 as trading capital to access premium training module. Profits can be withdrawn anytime. WhatsApp: +91 9123456789.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },
    {
        'title': 'Investment Operations Associate',
        'company_profile': 'Alpha Returns Capital Management',
        'description': 'Part-time investment operations role. Manage client portfolio entries. Fixed salary Rs 30,000 plus 5% of profits generated. Work from home, just 2 hours daily. Company provides trading platform access.',
        'requirements': 'Open a funded trading account with minimum Rs 25,000 deposit on our partner platform. Company will manage trades. Guaranteed minimum 10% monthly returns on your capital.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },

    # -- New: Government job scams --
    {
        'title': 'Government Data Entry Operator - SSC Recruitment',
        'company_profile': 'Staff Selection Commission (SSC) Recruitment Cell',
        'description': 'Direct recruitment for Data Entry Operator post under SSC. 7th CPC pay scale Rs 25,500 - Rs 81,100. No written exam needed for this special quota vacancy. Permanent government job with pension benefits.',
        'requirements': 'Class 12 pass. Apply by paying Rs 1,200 processing fee via UPI. Send Aadhaar, 10th and 12th marksheets to ssc.recruitment2024@gmail.com. Selection list released within 7 days.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },
    {
        'title': 'Railway Clerk - Direct Appointment',
        'company_profile': 'Indian Railway Recruitment Board',
        'description': 'Vacancy for Junior Clerk in Indian Railways. Monthly salary Rs 35,000. Direct appointment without examination under special discretionary quota. Limited seats available. Apply within 3 days.',
        'requirements': 'Graduation in any stream. Send passport size photo, Aadhaar copy, and application fee Rs 950 via Google Pay to +91 8899776655. Appointment letter will be couriered.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },
    {
        'title': 'पोस्ट ऑफिस भर्ती - सीधी नियुक्ति',
        'company_profile': 'भारतीय डाक विभाग',
        'description': 'भारतीय डाक में पोस्टमैन और मेल गार्ड पदों पर सीधी भर्ती। वेतन: ₹21,700 - ₹69,100। परीक्षा की जरूरत नहीं। सीमित सीटें उपलब्ध। तुरंत आवेदन करें।',
        'requirements': 'दसवीं पास। रजिस्ट्रेशन शुल्क ₹800 UPI से भेजें। आधार कार्ड और मार्कशीट WhatsApp करें: +91 9876543210।',
        'fraudulent': 1,
        'source': 'hard_examples'
    },

    # -- New: Hinglish scams (Roman-script Hindi) --
    {
        'title': 'Data Entry Work From Home',
        'company_profile': 'QuickTask Solutions',
        'description': 'Ghar baithe kaam karo aur Rs 25,000 mahine kamao. Simple data entry karna hai, daily 2-3 ghante. Koi experience ki zaroorat nahi. Paise directly bank account mein aayenge. Bahut log kama rahe hain.',
        'requirements': 'Laptop ya computer chahiye. Registration fee Rs 500 GPay pe bhejo. WhatsApp pe contact karo: +91 7890123456. Jaldi karo sirf 10 seats bachi hain.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },
    {
        'title': 'Online Form Filling Job',
        'company_profile': 'EasyMoney Digital Services',
        'description': 'Sirf form bharo aur paisa kamao. Har form ka Rs 50 milega. Din mein 100 form easily bhar sakte ho. Monthly income Rs 1,50,000 tak possible hai. Hamare already 10,000 members kama rahe hain. Koi boss nahi, apni marzi se kaam karo.',
        'requirements': 'Ek baar Rs 999 registration fee dena hoga, uske baad lifetime earning. Telegram pe join karo @EasyMoneyJobs. Admin se baat karo activation ke liye.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },
    {
        'title': 'Mobile Se Kaam Karo - Daily Payment',
        'company_profile': 'SmartWork India',
        'description': 'Mobile phone se simple tasks karo aur daily Rs 2000-5000 kamao. Tasks jaise app install, review likho, video dekho. Student ho ya housewife, sabke liye perfect. Lakho log already kama rahe hain hamari app se.',
        'requirements': 'Android phone chahiye. App download karo aur Rs 299 activation charge pay karo. Referral se extra Rs 100 per referral. WhatsApp: +91 6543210987.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },

    # -- New: Sophisticated fee-collection scams --
    {
        'title': 'Junior Research Analyst - McKinsey Partner Firm',
        'company_profile': 'Strategic Insight Partners (McKinsey Authorized Staffing)',
        'description': 'Rare opportunity to work with McKinsey engagement teams as an external research analyst. This role involves market sizing, competitive analysis, and slide deck preparation. CTC: 12-18 LPA. Remote-first position.',
        'requirements': 'MBA from Tier-1/Tier-2 B-school. To complete your application, a refundable pre-employment assessment fee of Rs 3,500 is required. This covers psychometric testing and background screening by our third-party vendor. Pay via secure link sent to your email. Contact: sip.recruiting@outlook.com.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },
    {
        'title': 'Medical Coding Specialist (Remote)',
        'company_profile': 'MedCode Global Solutions - a NASSCOM registered healthcare IT firm',
        'description': 'Hiring certified medical coders for US healthcare client projects. Salary Rs 45,000-65,000 per month. Work from home. Mandatory 2-week paid training included. Employment bond of 1 year.',
        'requirements': 'CPC/CCS certification preferred but not mandatory - training provided. Company will issue laptop after collection of Rs 4,000 refundable equipment deposit via bank transfer. Email: medcode.hr@gmail.com.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },
    {
        'title': 'Accounts Payable Executive',
        'company_profile': 'Nexus BPO Services',
        'description': 'Processing vendor invoices and payment reconciliation for Fortune 500 clients. Salary: Rs 28,000 fixed + incentives. Night shift (US timezone). Cab facility provided.',
        'requirements': 'B.Com graduate. Carry following for joining: Original degree certificate as security deposit (returned after employment bond period), Rs 1,500 ID badge processing fee, 6 passport photos. Contact: nexus.bpo.hr@yahoo.com.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },

    # -- New: Job scams targeting specific demographics --
    {
        'title': 'Housewife Special - Earn From Home',
        'company_profile': 'HomeIncome India',
        'description': 'Special work from home opportunity for housewives and women. Make decorative items, candles, or do simple packing work at home. Company will send raw materials. Earn Rs 15,000-30,000 per month in your free time. 500+ housewives already earning.',
        'requirements': 'No experience needed. Pay Rs 2,500 raw material advance deposit. Material kit delivered to your doorstep. Production training video on YouTube. WhatsApp: +91 8765432100.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },
    {
        'title': 'Student Internship - Earn While You Learn',
        'company_profile': 'FutureSkill Academy',
        'description': 'Paid internship for college students. Stipend Rs 8,000/month + industry certificate. Learn digital marketing, SEO, content writing. Add to your resume. Limited batch of 30 students only.',
        'requirements': 'Currently enrolled in any degree. Pay Rs 1,999 course material and certification fee. 100% placement assistance after internship. Apply: futureskill.intern@gmail.com.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },

    # -- New: Fake placement agency scams --
    {
        'title': 'Multiple Openings - Top MNCs',
        'company_profile': 'CareerBoost Placement Consultancy',
        'description': 'We have direct tie-ups with TCS, Infosys, Wipro, HCL, Accenture. Guaranteed placement within 15 days. Salary packages ranging from 3 LPA to 12 LPA. 100% placement record. Over 5000 students placed this year.',
        'requirements': 'B.Tech/BCA/MCA with any percentage. One-time placement service charge of Rs 5,000 (non-refundable). Interview coaching and resume building included. WhatsApp resume to +91 9876540123.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },
    {
        'title': 'IT Fresher Hiring Drive - Walk-in',
        'company_profile': 'TechHire Staffing Solutions',
        'description': 'Mega hiring drive for IT freshers. Companies participating: Cognizant, Capgemini, LTIMindtree, Persistent. Date: This Saturday. Venue: Hotel Grand, MG Road. Free lunch and travel allowance. Walk-in between 9 AM - 12 PM.',
        'requirements': 'Bring 5 copies of resume, all original certificates, and registration fee Rs 800. On-spot offer letters for selected candidates. Pre-register on WhatsApp: +91 8877665544.',
        'fraudulent': 1,
        'source': 'hard_examples'
    },

    # -- New: More hard negatives to balance --
    {
        'title': 'Machine Learning Engineer',
        'company_profile': 'Fractal Analytics is a leading AI company with offices in Mumbai, Bengaluru, London, and New York.',
        'description': 'We are looking for ML Engineers to join our AI team. You will work on NLP, computer vision, and recommendation systems for Fortune 500 clients. Competitive salary. Excellent benefits including health insurance, ESOPs, learning budget.',
        'requirements': 'M.Tech/PhD in CS/ML preferred. Strong Python, PyTorch/TensorFlow. Published research is a plus. Apply at https://fractal.ai/careers.',
        'fraudulent': 0,
        'source': 'hard_examples'
    },
    {
        'title': 'Product Designer - Urgent Hire',
        'company_profile': 'Razorpay Software Private Limited',
        'description': 'Urgent opening for Senior Product Designer. Immediate start preferred. Salary: 25-40 LPA based on experience. Remote-friendly with quarterly offsites. Join the team building India\'s leading payment infrastructure.',
        'requirements': 'Portfolio with fintech/B2B SaaS work. 4+ years experience. Figma mastery. Apply at https://razorpay.com/jobs.',
        'fraudulent': 0,
        'source': 'hard_examples'
    },
    {
        'title': 'BPO Customer Service Agent (Night Shift)',
        'company_profile': 'Teleperformance India',
        'description': 'International voice process for US healthcare client. Salary Rs 22,000 + night shift allowance Rs 3,000. Free cab facility. Rotational weekly off. Walk-in interviews Monday to Friday.',
        'requirements': 'Graduation not mandatory but preferred. Neutral English accent. Venue: Teleperformance Office, DLF Cyber City, Gurgaon. Carry resume and photo ID.',
        'fraudulent': 0,
        'source': 'hard_examples'
    },
    {
        'title': 'Social Media Manager',
        'company_profile': 'Zomato',
        'description': 'Looking for a Social Media Manager to handle our Instagram, Twitter, and LinkedIn presence. Known for our witty social media game - looking for someone who gets internet culture. Competitive compensation.',
        'requirements': 'Proven social media portfolio. Experience managing brand handles with 100K+ followers. Apply at https://www.zomato.com/careers.',
        'fraudulent': 0,
        'source': 'hard_examples'
    },
    {
        'title': 'Accounts Clerk',
        'company_profile': 'Mahindra & Mahindra Financial Services',
        'description': 'Hiring Accounts Clerks for branch operations. Salary Rs 20,000 - Rs 28,000. Fixed working hours. PF, ESI, Gratuity benefits. Multiple branch locations available across Maharashtra.',
        'requirements': 'B.Com with Tally knowledge. Apply through official Mahindra careers portal or send resume to hr.mmfsl@mahindra.com.',
        'fraudulent': 0,
        'source': 'hard_examples'
    },
    {
        'title': 'Paid Research Study Participant',
        'company_profile': 'UserTesting India (a division of UserTesting.com)',
        'description': 'Get paid for testing websites and mobile apps. Earn Rs 500-2000 per test session (20-60 minutes). Tests available weekly. Payment via PayPal or bank transfer. Flexible - complete tests whenever you want.',
        'requirements': 'Webcam and microphone. Sign up at https://www.usertesting.com/get-paid-to-test. No fees ever - you get paid, not the other way around.',
        'fraudulent': 0,
        'source': 'hard_examples'
    },
    {
        'title': 'DevOps Engineer',
        'company_profile': 'Atlassian',
        'description': 'Join the team behind Jira, Confluence, and Bitbucket. Looking for DevOps engineers to scale our cloud infrastructure. Competitive pay, RSUs, unlimited PTO policy. Bengaluru office with flexible hybrid model.',
        'requirements': 'Kubernetes, AWS/GCP, Terraform, CI/CD pipelines. 3+ years experience. Apply at https://www.atlassian.com/company/careers.',
        'fraudulent': 0,
        'source': 'hard_examples'
    },
]
