from flask import Flask, request, jsonify, render_template_string, session, g
import json
import os
import uuid
import time
import html
import re
from datetime import datetime
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger('chatbot')

# Simple rate limiting using in-memory storage (for single instance)
request_counts = {}
RATE_LIMIT_WINDOW = 60  # 1 minute
RATE_LIMIT_MAX = 10     # 10 requests per minute

def simple_rate_limit():
    """Simple rate limiting implementation"""
    client_ip = request.remote_addr
    current_time = time.time()
    
    # Clean old entries
    cutoff_time = current_time - RATE_LIMIT_WINDOW
    request_counts[client_ip] = [t for t in request_counts.get(client_ip, []) if t > cutoff_time]
    
    # Check if rate limit exceeded
    if len(request_counts.get(client_ip, [])) >= RATE_LIMIT_MAX:
        return True
    
    # Add current request
    if client_ip not in request_counts:
        request_counts[client_ip] = []
    request_counts[client_ip].append(current_time)
    
    return False

# Mock responses for 3MTT organization
MOCK_RESPONSES = {
    "dashboard_scores": "This is because your dashboard gradually syncs with your Darey.io and it may take some time for your Darey.io score to tally with that of your dashboard.",
    "program_end": "Cohort 3 ends July 20th.",
    "change_course": "Yes, you can change your course before you get admitted into the Learning Management System. Once you have been admitted, you won't be able to change your course. You can change your location at any given during cohort 3.",
    "onboarding_wait": "You will be added to communities where you will get access to free resources, collaborative self paced learning and physical meetup with your peers.",
    "entry_assessment": "Yes, there will be an entry assessment to determine the skill benchmark for each applicant. This will also be used in selecting the most applicable course for fellows.",
    "financial_support": "The only financial support for this phase of the programme will be the cost of training. Participants will be responsible for transportation, meals and other costs.",
    "physical_attendance": "The training is hybrid, meaning that it combines online and in-person components. While the majority of the training can be done remotely, there are aspects that will require in-person training.",
    "learning_community": "When you are assigned to a learning community in your location, the information will be displayed on your community page with the 3mtt portal when you log in.",
    "office hours": "Our office hours are Monday-Friday 9AM-6PM EST. We're closed on weekends and holidays.",
    "contact": "You can contact our support team for any 3MTT related inquiries.",
    "default": "Hello! Welcome to 3MTT support. How can I help you today? You can ask about dashboard scores, program timeline, course changes, assessments, or general support."
}

def contains_malicious_content(text):
    """Check for potentially malicious content"""
    malicious_patterns = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',                # JavaScript URLs
        r'on\w+\s*=',                 # Event handlers
        r'<iframe[^>]*>',             # Iframes
        r'<object[^>]*>',             # Objects
        r'<embed[^>]*>',              # Embeds
    ]
    
    text_lower = text.lower()
    for pattern in malicious_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True
    return False

def load_knowledge_base():
    """Load knowledge base from JSON file"""
    try:
        with open('knowledge_base.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("Knowledge base file not found. Using basic knowledge.")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Knowledge base JSON decode error: {e}")
        return {}

def flatten_dict_value(value, key_context=""):
    """Flatten dictionary values for better searching"""
    if isinstance(value, dict):
        result = []
        for k, v in value.items():
            if isinstance(v, str):
                result.append(f"{k}: {v}")
            elif isinstance(v, list):
                result.append(f"{k}: {', '.join(str(item) for item in v)}")
            else:
                result.append(f"{k}: {str(v)}")
        return "; ".join(result)
    elif isinstance(value, list):
        return ", ".join(str(item) for item in value)
    else:
        return str(value)

def search_knowledge_base(query, knowledge_base):
    """Search knowledge base for relevant information with better matching"""
    query_lower = query.lower()
    query_words = [word.strip() for word in query_lower.split() if len(word.strip()) > 2]
    
    # Define specific keyword mappings for better matching
    keyword_mappings = {
        'dashboard': ['dashboard', 'score', 'sync', 'darey', 'different'],
        'course': ['course', 'track', 'change', 'switch', 'program'],
        'assessment': ['assessment', 'test', 'exam', 'evaluation', 'entry'],
        'financial': ['financial', 'cost', 'fee', 'money', 'payment', 'support'],
        'timeline': ['end', 'finish', 'when', 'date', 'timeline', 'cohort'],
        'community': ['community', 'learning', 'group', 'assigned'],
        'support': ['support', 'help', 'contact', 'assistance', 'hours'],
        'onboarding': ['onboard', 'wait', 'waiting', 'start'],
        'platform': ['platform', 'portal', 'login', 'access']
    }
    
    # Score each section based on relevance
    section_scores = {}
    
    for section, content in knowledge_base.items():
        score = 0
        matched_content = []
        
        if isinstance(content, dict):
            for key, value in content.items():
                key_lower = key.lower()
                
                # Flatten complex values for better searching
                flattened_value = flatten_dict_value(value, key)
                value_str = flattened_value.lower()
                
                # Direct word matching
                for word in query_words:
                    if word in key_lower or word in value_str:
                        score += 2
                        content_key = f"{section}.{key}"
                        if content_key not in [item.split(': ')[0] for item in matched_content]:
                            # Use original value for display, not flattened
                            if isinstance(value, str):
                                matched_content.append(f"{content_key}: {value}")
                            else:
                                matched_content.append(f"{content_key}: {flattened_value}")
                
                # Keyword category matching
                for category, keywords in keyword_mappings.items():
                    if any(kw in query_lower for kw in keywords):
                        if any(kw in key_lower or kw in value_str for kw in keywords):
                            score += 3
                            content_key = f"{section}.{key}"
                            if content_key not in [item.split(': ')[0] for item in matched_content]:
                                if isinstance(value, str):
                                    matched_content.append(f"{content_key}: {value}")
                                else:
                                    matched_content.append(f"{content_key}: {flattened_value}")
        
        if score > 0:
            section_scores[section] = {'score': score, 'content': matched_content}
    
    # Return most relevant content
    if not section_scores:
        return []
    
    # Sort by score and return top matches
    sorted_sections = sorted(section_scores.items(), key=lambda x: x[1]['score'], reverse=True)
    relevant_info = []
    
    for section, data in sorted_sections[:2]:  # Top 2 sections
        relevant_info.extend(data['content'][:2])  # Top 2 items per section
    
    return relevant_info[:3]  # Maximum 3 items total

def get_ai_response(message, conversation_history=None):
    """Get response from OpenAI API with knowledge base context"""
    try:
        import openai
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.info("No OpenAI API key found. Using enhanced mock responses.")
            return get_enhanced_mock_response(message)
        
        client = openai.OpenAI(api_key=api_key)
        
        # Load knowledge base
        knowledge_base = load_knowledge_base()
        relevant_info = search_knowledge_base(message, knowledge_base)
        
        # Build enhanced system prompt with knowledge base
        knowledge_context = ""
        if relevant_info:
            # Extract clean information from search results
            clean_info = []
            for info in relevant_info:
                if ': ' in info:
                    clean_info.append(info.split(': ', 1)[1])
                else:
                    clean_info.append(info)
            knowledge_context = "\n".join(f"- {info}" for info in clean_info)
        
        system_content = f"""You are a friendly and knowledgeable customer support assistant for 3MTT (3 Million Technical Talent), Nigeria's flagship technical skills development program.

ABOUT 3MTT:
3MTT is part of Nigeria's Renewed Hope agenda, aimed at building the country's technical talent backbone to power the digital economy. The program has trained 30,000 fellows in Phase 1 (launched December 2023) and plans to train 270,000 more in Phase 2 across three cohorts.

{f"RELEVANT INFORMATION FOR THIS QUERY:{chr(10)}{knowledge_context}" if knowledge_context else ""}

INSTRUCTIONS:
- Be conversational, helpful, and empathetic
- Provide complete, coherent answers that make sense
- Use the context above to give accurate information
- If you don't have specific information, be honest about it
- Always aim to be helpful and guide users to solutions
- Keep responses natural and human-like, not robotic
- Don't just list facts - explain them in context"""

        messages = [{"role": "system", "content": system_content}]
        
        # Add recent conversation history for context
        if conversation_history:
            for conv in conversation_history[-5:]:  # Last 5 exchanges
                messages.append({"role": "user", "content": conv.get("user_message", "")})
                messages.append({"role": "assistant", "content": conv.get("bot_response", "")})
        
        messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model=os.getenv('AI_MODEL', 'gpt-4'),
            messages=messages,
            max_tokens=int(os.getenv('MAX_TOKENS', '300')),
            temperature=float(os.getenv('TEMPERATURE', '0.7'))
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"AI Error: {e}")
        return get_enhanced_mock_response(message)

def create_intelligent_response(message, knowledge_base):
    """Create intelligent, contextual responses based on user intent"""
    message_lower = message.lower()
    
    # Define response templates for different intents
    response_templates = {
        'program_overview': {
            'keywords': ['what is 3mtt', 'about 3mtt', 'tell me about', 'program overview', 'what is the program'],
            'response': lambda kb: f"{kb['3mtt_program']['overview']} The program is part of Nigeria's Renewed Hope agenda and aims to train technical talent across multiple phases. Phase 1 launched in December 2023 with 30,000 fellows, while Phase 2 will train 270,000 more technical talents."
        },
        'dashboard_issues': {
            'keywords': ['dashboard', 'score', 'sync', 'different', 'darey'],
            'response': lambda kb: f"Don't worry about dashboard score differences - this is completely normal! {kb['platform']['dashboard_sync']} The system automatically updates, so just give it some time to sync properly."
        },
        'course_changes': {
            'keywords': ['change course', 'switch course', 'course change', 'different course', 'can i switch', 'can i change'],
            'response': lambda kb: f"Yes, you can change your course, but timing matters! {kb['courses']['course_change_policy']} Also, {kb['courses']['location_change_policy']} So you have flexibility with location throughout the program."
        },
        'program_timeline': {
            'keywords': ['when end', 'program end', 'cohort end', 'finish', 'timeline'],
            'response': lambda kb: f"Cohort 3 ends on July 20th, 2024. The overall program runs for 12 months with different phases, and we're currently in an active phase of the program."
        },
        'financial_support': {
            'keywords': ['financial', 'money', 'cost', 'fee', 'payment', 'support'],
            'response': lambda kb: f"Here's what's covered financially: {kb['support']['financial_support']} The program covers your training costs, which is the main expense, but you'll need to handle your own transportation and meals for in-person sessions."
        },
        'available_courses': {
            'keywords': ['what courses', 'available tracks', 'course options', 'tracks available', 'what tracks', 'courses offer'],
            'response': lambda kb: f"We offer {len(kb['courses']['available_tracks'])} exciting tracks: {', '.join(kb['courses']['available_tracks'])}. Each track is designed to meet industry demands and help you build relevant skills for the digital economy."
        },
        'contact_support': {
            'keywords': ['contact', 'support', 'help', 'assistance', 'reach out'],
            'response': lambda kb: f"You can reach our support team through multiple channels: {', '.join(kb['support']['contact_methods'])}. Our office hours are {kb['support']['office_hours']}, and we're here to help with any 3MTT related questions!"
        },
        'onboarding_wait': {
            'keywords': ['waiting', 'onboard', 'when start', 'access'],
            'response': lambda kb: f"While you're waiting for full onboarding, you're not left empty-handed! {kb['onboarding']['waiting_period']} This gives you a head start on learning and connecting with your peers."
        },
        'assessments': {
            'keywords': ['assessment', 'test', 'exam', 'evaluation'],
            'response': lambda kb: f"Yes, there will be assessments! {kb['assessments']['entry_assessment']['purpose']} and they happen {kb['assessments']['entry_assessment']['timing']}. Don't worry - they're designed to help place you in the right track for your skill level."
        },
        'technical_issues': {
            'keywords': ['login', 'access', 'error', 'problem', 'trouble', 'issue', 'bug'],
            'response': lambda kb: f"I understand you're having technical difficulties. For login and access issues, please ensure you have a stable internet connection and are using a modern web browser as required. If the problem persists, please contact our support team through {', '.join(kb['support']['contact_methods'])} during our office hours: {kb['support']['office_hours']}."
        },
        'learning_community': {
            'keywords': ['community', 'group', 'peers', 'meetup', 'assigned'],
            'response': lambda kb: f"Great question about learning communities! {kb['support']['learning_communities']} {kb['onboarding']['community_assignment']} This helps you connect with fellow learners in your area for collaboration and support."
        },
        'program_phases': {
            'keywords': ['phase 1', 'phase 2', 'phases', 'cohort', 'fellows'],
            'response': lambda kb: f"The 3MTT program has multiple phases: Phase 1 launched in December 2023 with {kb['3mtt_progrt)rt=por0', po.0.ost='0.0g=False, hburun(de   app.
 ', 5002))RTon.get('POos.envirint(t = _':
    por__main__name__ == '

if _ics_html)tring(analytr_template_seturn rende  r
  ''html>
    'ody>
    </
    </b/p>><to Chat</a">← Back ef="/   <p><a hr   
           </div>
 v>
       </di     }
      :]])ations[-10 conversr conv in/p><hr>" fo]}...< '')[:100response',get('bot_conv.</strong> {Bot:rong>stp><..</p><}.100]age', '')[:t('user_messg> {conv.ge/strontrong>User:<n([f"<p><s   {"".joi     >
        "ing: 10px; #ddd; padd 1px solid; border:olly: screrflow-px; ovht: 300-heige="max<div styl      /h3>
      nversations<cent Co>Re        <h3ic">
    "metrdiv class=
        < v>
       /di
        </p>ative']}<counts['negntiment_{seative: Neg} | tral']['neunts_cou {sentimenttral:eu| Nitive']} 'poscounts[iment_sent {ositive:     <p>P       ution</h3>
t Distribtimen3>Sen          <h  ic">
"metrclass=div 
        <      
       </div>   ions)}</p>
ique_sessen(un>{l         <p3>
   /hsions<ue Ses  <h3>Uniq       ">
   s="metricas <div cl   
                </div>
/p>
    tions}<sal_converp>{tota  <      </h3>
    ationsl Conversota>T      <h3    >
  "metric" class=    <div  
    >
      h1tics</hatbot Analy>3MTT C    <h1dy>
    
    <bo/head> <e>
   /styl       <7bff; }}
 or: #00t: bold; colghwei24px; font-ont-size: argin: 0; f{ m { .metric p   
         #333; }}lor:; copx 0 10: 0 0rginh3 {{ maetric       .m}
      dius: 5px; }0; border-rapx  10 margin:ding: 15px; pad5f5f5;ground: #f {{ backicetr         .m  }}
 ing: 20px; o; padd aut0px: 50px; margindth: 80f; max-wins-serial, saamily: Arifont-f{    body {          <style>
       </title>
alyticst AnboT Chat <title>3MT
       <head>>
    
    <htmlYPE html>
    <!DOCT'' f'ytics_html =al 
    ans"))
   "anonymou on_id",sessi("(conv.getns.add_sessio unique       1
 tral")] +=, "neut"entimen("sv.getnts[connt_couentime      sons:
  nversatiin co   for conv 
    
 ns = set()ique_sessio    un": 0}
al 0, "neutrve": 0, "negatisitive":unts = {"poentiment_co
    sersations)n(conv letions =ersaal_convot  t
  nalytics  # Basic a
  
    ons = []onversati       cror:
 NDecodeErJSOpt json.exce
    ions = []  conversat     dError:
 NotFouncept File ex   (f)
adjson.lons = nversatioco          
   'r') as f:ns.json',onversatioopen('c  with      
 try:"""
    yticsn analversatioard for conshboda""Admin  "   ics():
 analyt
def)/analytics'ute('/admin)

@app.roessfully'}d succck collecteeedbassage': 'F 'mecess': True,sucy({'sonifrn jretu     
  : {e}")
 ve feedback to saled(f"Fair.error       logge e:
 xception as except E  
 dent=2), f, inining_datason.dump(tra         j
   w') as f:', 'ata.json('training_dwith open      
  try:   
 )
    end(feedbacka"].appfeedback_dating_data[" train
    
    []}gestions":_sugimprovement" [], ":dback_data[], "feees": xamplning_erai= {"tdata   training_or:
      codeErrSONDept json.J exce
   s": []}t_suggestion"improvemena": [], eedback_dat": [], "fesng_examplraini = {"tning_data     trai
   oundError: FileNotF  except(f)
  = json.loadta ning_da  trai      
    :, 'r') as fata.json'ining_dpen('tra     with o     try:
     
 )
    }
 Trueelpful',t('h data.gelpful":        "hext', ''),
back_teeedt('f data.ge_text":ck   "feedba    stars
  ng'),  # 1-5.get('ratig": data     "ratin,
   ')ponset('bot_res": data.gesespon "bot_re      ssage'),
 r_meata.get('usessage": der_me   "us
     ssage_id'),ata.get('meid": d"message_        id'),
et('session_ta.gd": da"session_i       
 oformat(),me.now().istetistamp": da     "time
   ack = {dbfeeon()
    t_jsst.ge = reque   data"""
 n responsesback ofeedt user lec"Col
    ""):back(llect_feedT'])
def coethods=['POSk', m/feedbacte('pp.rou@a)

esults}': rults'ressonify({urn j
    retase)wledge_by, knoe_base(querh_knowledgults = searc
    resbase()wledge_no load_kbase =edge_ knowl')
   uery', '.get('q = data    queryson()
est.get_ja = requ
    datrch"""e base seaest knowledg   """Tsearch():
  test_OST'])
defhods=['P, metch'test-sear/admin/oute('pp.rl)

@atmdge_hnowle(kte_stringtemplaender_ r
    returnl>
    ''' </htm
     </body>pt>
        </scri  }}
            });
       }      '');
   /p>').join(• ' + r + '<<p>(r => 'lts.mapesu   data.r                   ' + 
  sults:</h4>Reearch h4>S       '<         
         erHTML =lts').innresu('search-IdementByment.getEl    docu               
 a => {{  .then(dat             
 se.json())se => responen(respon        .th       
          }})  })
     ry: query }ngify({{ queON.striody: JS           b        ' }},
 sonplication/j'apent-Type': s: {{ 'Contader        he          POST',
   'ethod:     m         
      earch', {{in/test-stch('/adm          fe;
      aluequery').vt-entById('teslemument.getE query = docnst     co           ) {{
t(on searchTes functi            
   }}
                    }}
               sage);
 e.mesrmat: ' + ON foJSid lert('Inval        a          ) {{
  ch (e     }} cat          }});
                    eload();
 cation.ress) loata.succ(dif                        ge);
 a.messaalert(dat                        => {{
n(data he        .t           
 son())sponse.je => responsn(re       .the         
             }})          sed)
 ar.stringify(pbody: JSON                  
      /json' }},on'applicatit-Type': onteners: {{ 'C   head               ,
      POST': '  method                      {{
 ge',ledowadmin/knfetch('/                  );
  knowledgeN.parse( = JSOrsednst pa       co              try {{
             e;
  tor').valuowledge-ediknId('ElementBydocument.getwledge = nst kno    co            ) {{
edge(Knowlten upda   functio
          <script>
       
v>      </di/div>
  ;"><olid #dddpx sr: 1bordewhite; ound: ckgr; bapxadding: 10 pp: 10px;="margin-tolts" styleh-resu"searc   <div id=
         on>earch</butt">STest()ick="searchclutton on     <b  x;">
     10pding: padidth: 70%; le="wry..." styer test que="Enteholderplact-query" " id="tes"textype=ut t<inp            3>
arch</hge Sest Knowled   <h3>Te       tion">
  ="sec <div class 
       v>
            </di
   h</button>e Searcst Knowledg)">TestKnowledge(ick="te oncltton        <bu   on>
 Base</buttedge  Knowldate">Upe()edgateKnowl"updick=on onclbutt   <    br>
          <   rea>
    extadent=2)}</t, inbasee_ps(knowledg">{json.dumditorledge-eow="kna id   <textare    
     3>edge Base</h Knowl3>Current<h        
    ">sectionass="div cl  <   
        </h1>
   e Managementowledge Bas     <h1>Kn      
   
  >    </div</a>
    owledge Base>Knknowledge"n/ef="/admi hr    <a      a>
  >Analytics<//analytics"/admin"ef=hra            <t</a>
  Cha"/">← href=        <a   v">
 ass="na<div cl
            <body>  </head>

     </style>
     bff; }}olor: #007e; ction: nontext-decoraht: 15px; in-rig {{ marg    .nav a}}
        px; m: 20gin-bottoav {{ mar      .n       5px; }}
rgin:ter; maincursor: ponone;  border: olor: white;f; c#007bf: colorround-ackg0px; bpx 2g: 10 {{ paddin     button }}
       monospace;t-family: 0px; fon 40t:%; heighh: 100a {{ widt textare        }}
    x;radius: 5prder-bo 0; argin: 10px 15px; mdding: #f5f5f5; pakground:tion {{ bac    .sec}
        ing: 20px; }to; padd aumargin: 50px00px; x-width: 10 ma-serif;ial, sansily: Ar-famy {{ font bod        style>
     <      itle>
gement</tManawledge Base tle>3MTT Kno  <ti  d>
    hea
    <
    <html>CTYPE html>DO
    <!ml = f'''dge_ht knowle   
   e_base()
 nowledg= load_kse owledge_ba   knse
 wledge banod current koa
    # L tr(e)})
   ': ssage False, 'mesccess':onify({'su  return js          s e:
on aept Excepti   exc})
     uccessfully'dated sbase upedge age': 'KnowlmessTrue, 's': cces{'sunify(jsoeturn         rt=2)
    e, f, indenew_knowledgdump(njson.           f:
      'w') asase.json', ge_bpen('knowled  with o
            try:  
    json()quest.get_= reedge    new_knowl
     basewledge # Update kno  ':
      od == 'POSTst.methf reque"""
    iedge baseknowl managing terface for""Admin in
    "owledge():anage_kn])
def mET', 'POST'ethods=['Gedge', mnowl/admin/k@app.route(' 500

n.'}),ase try agaiccurred. Pleror oerxpected : 'An uney({'error'eturn jsonif  rdr})
      te_ad.remodr': requeste_ade), 'remot': str(ror, extra={'erpoint"in chat endted error ("Unexpecerrorgger.   loe:
     on as tit Excepexcep       
      })
 
  uid4())tr(uuid.ud': sage_i 'mess    
       _id'],on['sessionessi: sid''session_            _response,
otsponse': b        're    onify({
rn jsetu     r
   
        
        )         }me
   tisponse_e': rese_tim 'respon             ),
  bot_response: len(gth'se_len   'respon             ssage),
 len(user_meength':essage_l      'm          sion_id'],
ession['ses s_id':on'sessi                ,
'unknown')uest_id', reqr(g, 'getattd': _iquest       're
         extra={    ,
        ed"letion compnteract iat "Ch
           gger.info(lo
        rt_timeime() - sta= time.te_time ons       respaction
  chat inter successful      # Log          
sation
 the convern't saveif we cae request il thfa't        # Don)
     e)}: str(={'error'", extraversationoned to save crror("Fail   logger.e         s e:
n apt Exceptio     exce
   ession_id']) session['snse,pores bot_message,user_rsation(veone_c       sav   try:
  
        ingracksession tion with onversat c # Save       
  4())
      id.uuidr(uu'] = stion_idn['sess    sessio        session:
id' not in ession_   if 's ID
     essionor create s     # Get        
   
 moment."again in a ease try ght now. Plquest ri your re processingving troublery, I'm ha soronse = "I'mot_resp          b
  0]})[:10er_messagessage': us str(e), 'merror':, extra={'eiled"sponse fa reor("AIer.err    logg      e:
  tion as pt Excepexce      
  istory)_hnversation coessage,onse(user_m_ai_respgetnse = respo        bot_  :
        trycontext
  se with I respon AGet     #        
    []
 on_history =rsati    conve        )
tr(e)}rror': sxtra={'e", eations fileersrupted converror("Cor     logger.   
     e:Error asDecodeon.JSONexcept js
         []_history =conversation    
        r:NotFoundErropt File    exce)
    ad(fson.lo= jhistory ersation_    conv           ') as f:
 n', 'rs.jsonversationopen('co     with :
             try
  ntext for cotion historyd conversa      # Loa    
  400
    ected'}), etid content dr': 'Invalnify({'erroreturn jso       dr})
     st.remote_adque': rete_addremo], 'r[:100ssager_me usesage':ra={'mes, extd"tectecontent decious rning("Maliwa   logger.
         ge):er_messat(usontenious_cins_malicconta  if     
  ntents cofor maliciouy check urit   # Sec 
         
   e.strip())(user_messagescapetml.message = h user_      
 put inizeanit
        # S     , 400
   rs)'})haracte00 cax 10ong (m too lr': 'Messagerroonify({'e jsurnet r    })
       .remote_addrr': requestemote_addge), 'ressan(user_mngth': le'le extra={oo long",ge t("Messaning.wargger         lo000:
   ) > 1_messagef len(user      i      
  , 400
  ed'})ovido message pr 'Nor':nify({'errturn jso        ressage:
    _meot user        if ntion
idaInput val # 
       
        ge', '')messa('getage = data. user_mess         
     '}), 400
 JSON 'Invalid error':sonify({' j    return      dr})
  _adt.remoteddr': reques_aa={'remoted", extrJSON received ng("Invaliarniger.w   log
         ot data:      if n
  on()get_js = request.     data
    9
        42ent.'}),it a momse wasts. Pleay requer': 'Too man{'erronify( return jso  
         ote_addr})emest.requaddr': r{'remote_ed", extra=eedt excRate limi.warning("      logger:
      mit()te_lif simple_ra   i   k
  checimiting mple rate l# Siy:
          tr()
    
   time.time_time =start""
    g"rind monito anith securityt messages w"Handle cha""at():
    )
def chST']ds=['POthoat', me/chp.route(')

@aptmlng(hte_striender_templa    return r
    '''
</html>body>
    
    <//script>        <);
alse, f today?'n I help yout. How caupporme to 3MTT s! Welcolloage('He     addMess    essage
   lcome m// Add we             }

     
      age(); sendMesser')= 'Enty ==f (event.ke      i         ) {
 entyPress(evndleKeon hafuncti               }

     ));
    , falsen.' try agailease. Pongnt wrhing wemet'Sorry, soage(ess=> addMerror     .catch(           data))
 lse, fa, a.responsesage(dat addMes =>then(data       .         se.json())
ponse => resn(respon      .the
                  })       age })
 e: messagify({ mess.string JSONody:      b           n' },
   json/atiopplicpe': 'aent-Ty{ 'Cont: headers           
         d: 'POST',hoet        m            {
/chat', h('       fetc         ';

 = 'input.value           ue);
     ssage, trMessage(me        add

        return;ge) essa  if (!m             im();
 value.tre = input.const messag             ut');
   ssage-inpmentById('meetElent.g documeut = const inp             {
   ndMessage()function se     
            }
});
                       }
               
     se);al fack! 🙏',r feedbu for younk yo'Thassage(      addMe             ss) {
      (data.succe    if                
n(data => {        .the)
        n()jsoonse.=> respen(response      .th       })
                  )
      }            2
     lpful ? 5 :ating: he     r                  elpful,
 : hpfulhel                       esponse,
 se: lastBotR bot_respon                
       erMessage,: lastUsser_message          u             essageId,
 id: currentMage_ mess                   ,
    onIdurrentSessision_id: ces         s          
     ingify({dy: JSON.str          bo   
       /json' },ontipplica: 'atent-Type' { 'Con    headers:           T',
     method: 'POS               k', {
     /feedbactch('     fe            
              return;
  ageId)rrentMess    if (!cu            ful) {
helpFeedback(endnction s     fu  

     }           
 t;eighrollHContainer.sc chatllTop =.scroontainer  chatC             ;
 essageDiv)hild(mndCiner.appentaatCo        ch
                       }
        }
                         
    d;.session_i messageDataonId =rentSessi        cur              e_id;
  Data.messagessage msageId =entMes     curr                  a) {
 essageDat (m      if        age;
      ss = meBotResponse       last   
          ';'</div>                     +
    tton>'l</buHelpfupx;">👎 Not : 3radiusrder-ointer; boursor: px; c10pdding: 5px : none; pahite; borderolor: w: #dc3545; croundtyle="backgse)" sback(fal="sendFeedlickutton onc '<b             
          ton>' +l</butpfu">👍 Helius: 3px;er-rad; bordr: pointer5px; cursoight: n-rpx; margiding: 5px 10padone; r: nordewhite; b: 45; colorround: #28a7kgacstyle="btrue)" k("sendFeedbacick=utton oncl<b      '           
       px;">' +n-top: 10argistyle="miv        '<d            + 
      = messageinnerHTML ssageDiv.    me              else {
              }     sage;
age = messtUserMessla                sage;
     mesontent =v.textC   messageDi        
         (isUser) {        if      
             
      ' : 'bot');r ? 'user' + (isUseessage Name = 'mgeDiv.class    messa      
      iv');('dElementate.cre documenteDiv =messag    const             r');
t-containehayId('ctElementBment.geainer = docuhatCont  const c        {
      ta = null)  messageDa, isUser,sage(messageddMes function a          '';

  ponse =lastBotRes   let         age = '';
 stUserMess  let la    l;
       nulId =entSessionet curr      l    l;
  ageId = nulurrentMess       let cipt>
      <scr      

 /div>
        <n>tto)">Send</buendMessage(lick="soncutton" -bsendd="n i  <butto       
   ">vent)Press(ehandleKeynkeypress="e..." or messag="Type you placeholder"e-input id="messagype="text"   <input t        er">
 put-contain"indiv id=       <>
 "></divntainerat-cod="ch     <div ih1>
   t Chat</orupp  <h1>3MTT S  body>
        <
d>>
    </heatyle       </ster; }
 cursor: poinone;  border: n: white;7bff; color: #00olornd-c backgrou0px 20px;dding: 1 paon {d-butt #sen     d; }
       solid #dd 1px0px; border:ding: 1ex: 1; pad-input { fl #message          lex; }
 y: fispla{ dcontainer   #input-     
      } #f5f5f5;round-color:t { backg  .bo
          ight; }t-align: r2fd; texlor: #e3fd-cobackgrounser {          .ux; }
   -radius: 5porder8px; bdding: 0px 0; pa: 1gine { mar.messag      }
       0px;bottom: 1px; margin- padding: 10roll;rflow-y: sc400px; oveght: ; heisolid #dddder: 1px ainer { borchat-cont          #}
  ding: 20px; px auto; padin: 50 marg 600px;dth:f; max-wi sans-seriily: Arial,fam{ font-  body         >
  yle <st    e>
   </titlport Chat>3MTT Supitle<t         <head>
 
  ml><ht  ml>
  !DOCTYPE ht'''
    < = "
    html" interface"he chaterve t
    """Sex(): ind)
defp.route('/'aps_code

@tatu, status)_sealthn jsonify(htur   relse 503
 thy' es'] == 'healatu'sttus[stalth_heaif code = 200    status_GB'
    
 b:.2f}e_gac_splthy: {free'heapace'] = fks']['disk_satus['chec health_stse:
       '
    el 'degradedtatus'] =atus['slth_st        hea
2f}GB'e_space_gb:.w: {fre'] = f'lok_spacecks']['diss['chestatu  health_ 1:
      ace_gb <ree_spif f3)
    24**e / (10.fre= disk_usage_gb pace free_s)
   usage('.'til.disk_ = shusk_usageil
    dimport shutace
    i disk spheck
    # C'
    nfigured = 'not_corvice']ks']['ai_seatus['checalth_sthe        
se:  el
  ed'nfigur] = 'coservice']['ai_ks'ec['chalth_status       hePI_KEY'):
 OPENAI_Aenv('etos.gif ervice
    AI s Check 
    
    #ed'egrad = 'dtatus']s['stu health_sta     tr(e)}'
  {shealthy: ] = f'unledge_base'']['knows['checksth_statu    healas e:
     Exception xcept
    ehy'ealt] = 'hedge_base'wlecks']['knochth_status['al       hed(f)
 oa json.l
           r') as f:n', 'jsoe_base.owledgn('knwith ope        try:
   ase
 wledge bheck kno# C   
    
 }
    }checks': {       ''1.0.0',
 ion': 'vers   (),
     rmat.isofotetime.now()mp': daimesta
        'ty',': 'healthtus  'sta      = {
 tatusealth_s    h""
nitoring" for mopointndalth check e"""He):
    ck( health_che
deflth')te('/hea

@app.rourn response
    retu  )
     }
                gth
 content_lense. respon':thent_leng  'cont           _time,
   sponseime': reponse_t       'res
         tatus_code,se.s: responstatus_code'        '    wn'),
    ', 'unkno'request_id getattr(g, _id':est       'requ{
           extra=         ted",
 pleuest com"Req           er.info(
         loggart_time
me() - g.st.tiime_time = tresponse        time'):
, 'start_attr(gf hasonse
    i resp 
    # Log)
       'self'"
ct-src     "conne  
   data:; "c 'self'  "img-sr"
      e'; -inlinelf' 'unsafesrc 's"style-       ; "
 line'afe-in'unsf' el-src 'sscript      "'; "
  c 'self"default-sr     (
    ] =y'Polic-Security-s['Contentersponse.head
    rety Policyent Securiont
    # C  '
  ode=block '1; m =rotection']-Pders['X-XSSse.hearespon  = 'DENY'
  s'] e-OptionFramrs['X-nse.headespoiff'
    resn = 'no']ype-Optionstent-TConheaders['X-   response.eaders
 y h  # Securitse"""
  og responders and leaty hsecuri """Add se):
   t(responeser_requef aft_request
dpp.after
    )

@a}       100]
 ', '')[:ntUser-Ageers.get('uest.headt': reqer_agen    'us      
  ddr,remote_aquest._addr': remote    're,
        .endpointequestpoint': r      'end     hod,
 uest.metmethod': req   '       d,
  equest_i: g.ruest_id'  'req          xtra={
,
        etarted"st sque    "Refo(
      logger.in   
  est)}"
 d(requ)}-{itime.time()nt("{iuest_id = freq)
    g.ime.time(ime = t g.start_t   """
d request IDtime and adst start ck reque"Tra
    ""():re_requestefoest
def be_requapp.befor

@")sation: {e}ave conver to siledr(f"Far.errologge   e:
     as xception cept Eex    =2)
s, f, indentconversationon.dump(         js   :
as fn', 'w') .jsoonversationsopen('c      with y:
     tron)
    
 nversatins.append(coersatioconv   
    s = []
 tion   conversa)
     "g freshstartin, ns.json filenversatiorrupted coerror("Co logger.     r:
  roSONDecodeEr json.Jexcept
    ations = [] convers:
       ErrorileNotFoundt Fxcep
    e(f) json.loadsations =   conver
         s f:r') ans.json', 'nversatioopen('coth  wiry:
         
    t  
    }
message): len(user__length"   "messageage),
     nt(user_messtime_sen analyzet":timen"sen       onse,
 ": bot_respespons "bot_re     message,
  : user_e"ag_messuser    "",
    mous"anonyion_id or _id": sess   "session   ,
  oformat()ime.now().isdatettamp": "times
         { =ersation conva"""
   datetaenhanced mfile with N SOrsation to J conveSave  """:
  n_id=None) sessio_response,e, botser_messagtion(u_conversa save

def"neutral"   return :
        elsegative"
  return "ne       :
tive_countt > posiune_co negativif
    elve""positireturn         ive_count:
unt > negat positive_co   if 
 
   r)sage_loweord in mesords if wve_wn negati for word iunt = sum(1 negative_co   ge_lower)
rd in messaords if woositive_wr word in pfoum(1 nt = se_cou   positiv()
 eressage.lowower = mmessage_l  ]
    
  e', 'error'issu, ' 'problem'ed',ppointted', 'disastra, 'fruul', 'angry'le', 'awfrribbad', 'tewords = ['negative_ul']
    , 'helpf'thanks''thank', ed', isfi 'sathappy',, 'nt'llet', 'excegrea', 'goodds = ['ve_wor
    positi"s""nt analysisic sentime  """Ba  ge):
t(messantimensealyze_ anlt"]

deffauSPONSES["den MOCK_RE       returelse:
   tact"]
  S["conRESPONSECK_MOrn   retu      ]):
support", "l"ne", "emai"phoact", ontd in ["cworer for essage_lown mf any(word i    elis"]
urice hooffRESPONSES["n MOCK_      retur  se"]):
lo", "cpen "o",s", "timed in ["hourr for worge_lowein messad  any(wor
    elifram_end"]ES["progOCK_RESPONSrn M     retun"]):
   "whem", , "progra"cohort", inish" "f["end",rd in  wor fore_lowe messag inrdf any(wo]
    elimunity"g_comninlear["ONSESOCK_RESP   return M    ing"]):
 "learnty", communi" in [or wordge_lower fd in messaf any(wor    elice"]
attendan"physical_SES[ONn MOCK_RESP      retur:
  rson"])", "petorynda", "matendanceical", "atn ["physr word ifoe_lower n messagf any(word i"]
    eliort_suppinancialSES["fOCK_RESPON    return M"]):
    oney"meal", "mt", ansportr", "nancialin ["fi for word age_lowerord in mess  elif any(wment"]
  ssessry_aS["entOCK_RESPONSErn Metu
        ram"]): "ex "test",, "entry",ssessment"["ain  word ge_lower ford in messany(worf a    eliit"]
_waonboardingNSES["POn MOCK_RESur  ret
      "]):it, "wang"itid", "wan ["onboard ier for worssage_lowin meny(word   elif arse"]
  ou"change_cSES[K_RESPON return MOC       
ish"]):in"end", "fd in [ for worage_lower messrd inwoany( and not "]) "location"course",e", "changword in [for er age_lown messd i(woranylif     ees"]
d_scoroarNSES["dashb_RESPOMOCKurn et    r   :
 ])ifferent""sync", "d", "dareycore", rd", "s"dashboa [rd inower for won message_lword i   if any(.lower()
 er = message message_low  ""
 tent"ssage con based on mesponsemock reppropriate urn a""Rete):
    "nse(messagock_respoget_m

def sage)ponse(mesck_resurn get_mo ret       else:
)
    owledge_basesage, knresponse(mesintelligent_n create_tur
        ree_base: knowledg if  
    
 _base()wledgeoad_kno_base = l  knowledge""
  ponses"xtual resgent, conteintellie with mock responsnced   """Enha:
  e)messagesponse(ock_rnced_met_enhage)

def gsponse(messack_reeturn get_mo
    ronsesrespal mock k to origin # Fallbac    
   
age)(messck_responsen get_mo   retur    ")
     ase key: {e}wledge bissing knor.error(f"M     logge e:
       KeyError asexcept       _base)
  nowledge'](kesponseatch]['rbest_mtemplates[ponse_ res   return       try:
  
         > 0:hes_matcnd maxst_match a  if be
  t matchon bes based te responseera
    # Genent
    match = int      best_ches
      es = mattch max_ma      s:
     tchees > max_mamatchf        iower)
 in message_lkeyword '] if eywordsnfig['k coeyword infor kes = sum(1 ch   mat
     es.items():_templatin responset, config  inten   for  
 = 0
  tches max_ma    tch = None
ma   best_ntent
 g iest matchin b # Find the
    
       }   }

     ucture']}."'stre_2'][]['phasgram'rokb['3mtt_p']} in {et]['targ']['phase_2'3mtt_programg {kb['etinargen bigger, t be evillhase 2 w}. Ppproach']_a]['training]['phase_1'mtt_program''3{kb[nd included ]} aount'fellows_cphase_1']['am']['