from flask import Flask, Response
import os

app = Flask(__name__)

@app.route("/")
def home():
    html = """
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>HeroBoard – Community Service & Announcements</title>

        <!-- Google Font -->
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap" rel="stylesheet">

        <!-- Tailwind config BEFORE CDN -->
        <script>
          window.tailwind = {
            config: {
              theme: { extend: { fontFamily: { display: ['Poppins','ui-sans-serif','system-ui'] } } }
            }
          };
        </script>
        <script src="https://cdn.tailwindcss.com"></script>

        <!-- React (production UMD) + Babel -->
        <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
        <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
        <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
      </head>
      <body class="bg-slate-50 font-display text-[17px] sm:text-[18px]">
        <div id="root">Loading…</div>

        <!-- JSX compiler -->
        <script type="text/babel" data-presets="react">
          const { useState, useEffect, useMemo } = React;

          function App() {
            // current user (who am I?)
            const [user, setUser] = useState(() => localStorage.getItem("acton_user") || "");
            useEffect(() => { localStorage.setItem("acton_user", user); }, [user]);

            const [activeTab, setActiveTab] = useState("board"); // 'board' | 'ann'

            return (
              <div className="min-h-screen">
                <HeroHeader />
                <div className="max-w-6xl mx-auto px-4 sm:px-6">
                  <TopBar
                    user={user}
                    setUser={setUser}
                    activeTab={activeTab}
                    setActiveTab={setActiveTab}
                  />
                  {activeTab === "board"
                    ? <CommunityServiceBoard currentUser={user} />
                    : <AnnouncementsBoard currentUser={user} />}
                  <Footer />
                </div>
              </div>
            );
          }

          function HeroHeader() {
            return (
              <div className="bg-gradient-to-r from-indigo-500 via-fuchsia-500 to-rose-500 text-white">
                <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 sm:py-10">
                  <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight">HeroBoard</h1>
                  <p className="mt-2 text-white/90 text-lg">Community Service Board & Announcements.</p>
                </div>
              </div>
            );
          }

          function TopBar({ user, setUser, activeTab, setActiveTab }) {
            return (
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 -mt-8 sm:-mt-10 mb-6">
                <div className="bg-white shadow-lg rounded-2xl p-1 inline-flex">
                  <TabButton active={activeTab === "board"} onClick={() => setActiveTab("board")}>Community Service</TabButton>
                  <TabButton active={activeTab === "ann"} onClick={() => setActiveTab("ann")}>Announcements</TabButton>
                </div>

                <div className="bg-white border rounded-2xl shadow px-3 py-2 flex items-center gap-2">
                  <span className="text-slate-500 text-sm">I am</span>
                  <input
                    value={user}
                    onChange={(e)=>setUser(e.target.value)}
                    placeholder="your name"
                    className="px-3 py-2 border rounded-xl text-sm"
                    style={{minWidth:"12rem"}}
                  />
                </div>
              </div>
            );
          }

          function TabButton({ active, children, onClick }) {
            return (
              <button
                onClick={onClick}
                className={"px-4 sm:px-6 py-2 rounded-xl text-base font-semibold transition " +
                  (active ? "bg-slate-900 text-white shadow" : "text-slate-600 hover:bg-slate-100")}
              >
                {children}
              </button>
            );
          }

          function Footer() { return <div className="py-10 text-center text-sm text-slate-400">Made with ❤️ for Acton.</div>; }

          // -------- Community Service Board --------
          function CommunityServiceBoard({ currentUser }) {
            const [posts, setPosts] = useState(() => {
              const saved = localStorage.getItem("acton_cs_posts");
              if (saved) return JSON.parse(saved);
              return [
                { id: crypto.randomUUID(), type: "student", creatorName: "Rafci", area: "Khan",  day: "19 de ago", time: "C.C 11:00", location: "C.C", notes: "", slots: 1, signups: [], createdAt: Date.now(), owner: "Rafci" },
                { id: crypto.randomUUID(), type: "student", creatorName: "Paul",  area: "Khan",  day: "19 de ago", time: "C.C",        location: "C.C", notes: "", slots: 1, signups: [], createdAt: Date.now(), owner: "Paul" },
                { id: crypto.randomUUID(), type: "student", creatorName: "Anika", area: "Vocab", day: "21 de ago", time: "C.C",        location: "C.C", notes: "", slots: 1, signups: [], createdAt: Date.now(), owner: "Anika" },
                { id: crypto.randomUUID(), type: "guide",   creatorName: "Guide Team", area: "Library sorting", day: "Fri", time: "10:30–11:30", location: "Library", notes: "Need 2 volunteers", slots: 2, signups: [], createdAt: Date.now(), owner: "Guide Team" },
              ];
            });
            const [showForm, setShowForm] = useState(false);
            const [formDefaults, setFormDefaults] = useState(null);
            const [query, setQuery] = useState("");
            const [typeFilter, setTypeFilter] = useState("all");
            const [signTarget, setSignTarget] = useState(null); // opens big centered modal

            useEffect(()=>{ localStorage.setItem("acton_cs_posts", JSON.stringify(posts)); },[posts]);

            const filtered = useMemo(()=>{
              const q = query.trim().toLowerCase();
              return posts
                .filter(p => typeFilter==="all" ? true : p.type===typeFilter)
                .filter(p => !q ? true : [p.creatorName,p.area,p.day,p.time,p.location,p.notes].join(" ").toLowerCase().includes(q))
                .sort((a,b)=>b.createdAt-a.createdAt);
            },[posts, query, typeFilter]);

            function addOrUpdate(post){
              const withOwner = { owner: post.owner || currentUser || post.creatorName || "unknown", ...post };
              setPosts(prev=>{
                const idx = prev.findIndex(x=>x.id===withOwner.id);
                if(idx===-1) return [withOwner, ...prev];
                const next=[...prev]; next[idx]=withOwner; return next;
              });
              setShowForm(false); setFormDefaults(null);
            }
            function remove(id){
              setPosts(prev=>prev.filter(p=>p.id!==id));
            }
            function signUp(post, name){
              if(!name) return;
              const already = post.signups.some(s=>s.toLowerCase()===name.toLowerCase());
              if(already) return alert("You already signed up for this.");
              if(post.signups.length>=(post.slots||1)) return alert("Slots are full.");
              addOrUpdate({ ...post, signups:[...post.signups, name] });
            }
            function exportCSV(){
              const header=["Type","Creator","Area","Day","Time","Location","Slots","Signups","Notes","Owner"];
              const rows = posts.map(p=>[p.type,p.creatorName,p.area,p.day,p.time,p.location||"",p.slots||1,p.signups.join("; "), (p.notes||"").replaceAll(",", ";"), p.owner||""]);
              const csv=[header,...rows].map(r=>r.join(",")).join("\\n");
              const blob=new Blob([csv],{type:"text/csv;charset=utf-8;"}); const url=URL.createObjectURL(blob);
              const a=document.createElement("a"); a.href=url; a.download="community_service_board.csv"; a.click(); URL.revokeObjectURL(url);
            }

            return (
              <div className="-mt-2">
                <div className="flex flex-wrap items-center gap-3 mb-4">
                  <button onClick={()=>setShowForm(true)} className="px-4 py-2 rounded-2xl bg-indigo-600 text-white shadow hover:bg-indigo-700">+ New Post</button>
                  <button onClick={exportCSV} className="px-4 py-2 rounded-2xl bg-white border shadow hover:bg-slate-50">Export CSV</button>

                  <div className="ml-auto grid gap-3 sm:grid-cols-3 w-full sm:w-auto">
                    <input
                      placeholder="Search name, area, day, time, location…"
                      value={query} onChange={e=>setQuery(e.target.value)}
                      className="sm:col-span-2 px-3 py-2 rounded-xl border shadow-sm focus:outline-none focus:ring w-full"
                    />
                    <select value={typeFilter} onChange={(e)=>setTypeFilter(e.target.value)} className="px-3 py-2 rounded-xl border shadow-sm">
                      <option value="all">All posts</option>
                      <option value="student">Community cervice</option>
                      <option value="guide">Extra jobs</option>
                    </select>
                  </div>
                </div>

                <div className="overflow-x-auto rounded-2xl shadow ring-1 ring-slate-200 bg-white">
                  <table className="w-full text-left">
                    <thead className="bg-slate-100 text-slate-700 text-sm">
                      <tr>
                        <Th>Role</Th><Th>Eagle / Creator</Th><Th>Area of Help</Th><Th>Day</Th><Th>Time</Th><Th>Location</Th><Th>Sign ups</Th><Th>Actions</Th>
                      </tr>
                    </thead>
                    <tbody className="text-[16px]">
                      {filtered.length===0 && (<tr><td colSpan={8} className="py-10 text-center text-slate-400">No posts yet. Click “New Post”.</td></tr>)}
                      {filtered.map(p => (
                        <Row
                          key={p.id}
                          post={p}
                          currentUser={currentUser}
                          onEdit={()=>{ setFormDefaults(p); setShowForm(true); }}
                          onDelete={()=>remove(p.id)}
                          onOpenSignUp={()=>setSignTarget(p)}
                        />
                      ))}
                    </tbody>
                  </table>
                </div>

                {showForm && (
                  <PostForm
                    defaults={formDefaults}
                    onClose={()=>{ setShowForm(false); setFormDefaults(null); }}
                    onSave={post=>addOrUpdate(post)}
                    currentUser={currentUser}
                  />
                )}

                {signTarget && (
                  <SignUpModal
                    onClose={()=>setSignTarget(null)}
                    onConfirm={(name)=>{ signUp(signTarget, name); setSignTarget(null); }}
                    full={(signTarget.signups?.length||0) >= (signTarget.slots||1)}
                  />
                )}
              </div>
            );
          }

          function Th({ children }) { return <th className="px-3 py-3 font-semibold uppercase tracking-wide">{children}</th>; }

          function Row({ post, currentUser, onEdit, onDelete, onOpenSignUp }) {
            const full = (post.signups?.length || 0) >= (post.slots || 1);
            const canDelete =
              currentUser &&
              post.owner &&
              currentUser.trim().toLowerCase() === post.owner.trim().toLowerCase();
            return (
              <tr className="border-t">
                <td className="px-3 py-3 align-top">
                  <span className={"inline-flex items-center gap-1 px-2.5 py-1.5 rounded-xl text-xs font-semibold " + (post.type==="guide" ? "bg-amber-100 text-amber-800" : "bg-emerald-100 text-emerald-800")}>
                    {post.type==="guide" ? "Extra job" : "Community cervice"}
                  </span>
                </td>
                <td className="px-3 py-3 align-top font-semibold text-slate-800">{post.creatorName}</td>
                <td className="px-3 py-3 align-top">{post.area}</td>
                <td className="px-3 py-3 align-top">{post.day}</td>
                <td className="px-3 py-3 align-top">{post.time}</td>
                <td className="px-3 py-3 align-top">{post.location || "—"}</td>
                <td className="px-3 py-3 align-top">
                  <div className="flex flex-wrap gap-1">
                    {(post.signups || []).map((s,i)=>(<span key={i} className="px-2 py-0.5 rounded-xl bg-slate-100 text-slate-700 text-xs">{s}</span>))}
                    {post.signups?.length===0 && <span className="text-slate-400 text-sm">No signups yet</span>}
                  </div>
                  <div className="text-xs text-slate-400 mt-1">Slots: {post.signups?.length || 0}/{post.slots || 1} {full && <span className="text-rose-500 font-semibold">(Full)</span>}</div>
                </td>
                <td className="px-3 py-3 align-top">
                  <div className="flex flex-wrap gap-2">
                    <button
                      disabled={full}
                      onClick={onOpenSignUp}
                      className={"px-2.5 py-1.5 rounded-lg text-xs shadow " + (full ? "bg-slate-200 text-slate-500" : "bg-slate-900 text-white hover:shadow-md")}
                    >
                      {full ? "Full" : "Sign up"}
                    </button>
                    <button onClick={onEdit} className="px-2.5 py-1.5 rounded-lg border text-xs hover:bg-slate-50">Edit</button>
                    {canDelete && (
                      <button onClick={onDelete} className="px-2.5 py-1.5 rounded-lg border text-xs hover:bg-rose-50 text-rose-600">Delete</button>
                    )}
                  </div>
                  {post.owner && <div className="text-[11px] text-slate-400 mt-1">Owner: {post.owner}</div>}
                  {post.notes && <div className="text-xs text-slate-500 mt-1">{post.notes}</div>}
                </td>
              </tr>
            );
          }

          // Big centered sign-up modal
          function SignUpModal({ onClose, onConfirm, full }) {
            const [name, setName] = useState("");
            return (
              <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
                <div className="w-full max-w-md bg-white rounded-3xl shadow-2xl p-6">
                  <h3 className="text-2xl font-extrabold mb-1">Sign up</h3>
                  <p className="text-slate-500 mb-4">Enter your name to reserve a spot.</p>
                  <input
                    value={name}
                    onChange={(e)=>setName(e.target.value)}
                    placeholder="Your name"
                    className="w-full px-4 py-3 border rounded-2xl text-lg"
                    disabled={full}
                  />
                  <div className="flex justify-end gap-3 mt-6">
                    <button className="px-4 py-2 rounded-2xl border" onClick={onClose}>Cancel</button>
                    <button
                      className={"px-5 py-2 rounded-2xl text-white " + (full ? "bg-slate-300" : "bg-emerald-600 hover:bg-emerald-700")}
                      onClick={()=>{ if(!full) onConfirm(name.trim()); }}
                      disabled={full}
                    >
                      {full ? "Slots Full" : "Confirm"}
                    </button>
                  </div>
                </div>
              </div>
            );
          }

          function PostForm({ defaults, onSave, onClose, currentUser }) {
            const [type, setType] = useState(defaults?.type || "student");  // student (Community cervice) or guide (Extra job)
            const [creatorName, setCreatorName] = useState(defaults?.creatorName || (currentUser || ""));
            const [area, setArea] = useState(defaults?.area || "");
            const [day, setDay] = useState(defaults?.day || "");
            const [time, setTime] = useState(defaults?.time || "");
            const [location, setLocation] = useState(defaults?.location || "");
            const [slots, setSlots] = useState(defaults?.slots || 1);
            const [notes, setNotes] = useState(defaults?.notes || "");

            return (
              <div className="fixed inset-0 z-20 flex items-center justify-center bg-black/30 p-4">
                <div className="w-full max-w-2xl bg-white rounded-2xl shadow-xl p-5">
                  <div className="flex items-start justify-between mb-3">
                    <h2 className="text-xl font-bold">{defaults ? "Edit Post" : "New Post"}</h2>
                    <button onClick={onClose} className="px-2.5 py-1.5 rounded-lg border text-xs">Close</button>
                  </div>
                  <div className="grid sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs text-slate-500 mb-1">Post type</label>
                      <select value={type} onChange={(e)=>setType(e.target.value)} className="w-full px-3 py-2 border rounded-xl">
                        <option value="student">Community cervice</option>
                        <option value="guide">Extra job</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs text-slate-500 mb-1">Eagle / Creator name</label>
                      <input value={creatorName} onChange={(e)=>setCreatorName(e.target.value)} className="w-full px-3 py-2 border rounded-xl" />
                    </div>
                    <div>
                      <label className="block text-xs text-slate-500 mb-1">Area of help</label>
                      <input value={area} onChange={(e)=>setArea(e.target.value)} placeholder="e.g., Khan / Vocab / Library / Garden" className="w-full px-3 py-2 border rounded-xl" />
                    </div>
                    <div>
                      <label className="block text-xs text-slate-500 mb-1">Day</label>
                      <input value={day} onChange={(e)=>setDay(e.target.value)} placeholder="e.g., 21 de ago / Mon" className="w-full px-3 py-2 border rounded-xl" />
                    </div>
                    <div>
                      <label className="block text-xs text-slate-500 mb-1">Time</label>
                      <input value={time} onChange={(e)=>setTime(e.target.value)} placeholder="e.g., 11:00–11:30" className="w-full px-3 py-2 border rounded-xl" />
                    </div>
                    <div>
                      <label className="block text-xs text-slate-500 mb-1">Location</label>
                      <input value={location} onChange={(e)=>setLocation(e.target.value)} placeholder="e.g., C.C, Library, Studio" className="w-full px-3 py-2 border rounded-xl" />
                    </div>
                    <div>
                      <label className="block text-xs text-slate-500 mb-1">Slots (max volunteers)</label>
                      <input type="number" min={1} value={slots} onChange={(e)=>setSlots(parseInt(e.target.value||"1"))} className="w-full px-3 py-2 border rounded-xl" />
                    </div>
                    <div className="sm:col-span-2">
                      <label className="block text-xs text-slate-500 mb-1">Notes (optional)</label>
                      <textarea rows={3} value={notes} onChange={(e)=>setNotes(e.target.value)} placeholder="Any extra info, materials to bring, etc." className="w-full px-3 py-2 border rounded-xl" />
                    </div>
                  </div>
                  <div className="flex justify-end gap-2 mt-4">
                    <button onClick={onClose} className="px-3 py-2 rounded-xl border">Cancel</button>
                    <button onClick={()=>{
                      if(!creatorName || !area){ alert("Please fill at least Creator and Area."); return; }
                      const post = {
                        id: (typeof defaults?.id!=="undefined" ? defaults.id : crypto.randomUUID()),
                        type,
                        creatorName: creatorName.trim(),
                        area: area.trim(),
                        day: day.trim(),
                        time: time.trim(),
                        location: location.trim(),
                        slots: Math.max(1, slots||1),
                        signups: defaults?.signups || [],
                        notes: notes.trim(),
                        createdAt: defaults?.createdAt || Date.now(),
                        owner: (defaults?.owner) || (currentUser || creatorName || "unknown"),
                      };
                      onSave(post);
                    }} className="px-3 py-2 rounded-xl bg-slate-900 text-white">Save</button>
                  </div>
                </div>
              </div>
            );
          }

          // -------- Announcements (Instagram-style cards) --------
          function AnnouncementsBoard({ currentUser }) {
            const [items, setItems] = useState(()=>{
              const saved = localStorage.getItem("acton_announcements");
              return saved ? JSON.parse(saved) : [];
            });
            const [show, setShow] = useState(false);
            const [def, setDef] = useState(null);

            useEffect(()=>{ localStorage.setItem("acton_announcements", JSON.stringify(items)); },[items]);

            function save(it){
              const withOwner = { owner: (def?.owner) || (currentUser || "unknown"), ...it };
              setItems(prev=>{
                const idx = prev.findIndex(x=>x.id===withOwner.id);
                if(idx===-1) return [withOwner, ...prev];
                const next=[...prev]; next[idx]=withOwner; return next;
              });
              setShow(false); setDef(null);
            }
            function remove(id){ setItems(prev=>prev.filter(x=>x.id!==id)); }

            return (
              <div className="-mt-2">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-2xl font-extrabold text-slate-800">Announcements</h2>
                  <button onClick={()=>{ setDef(null); setShow(true); }} className="px-4 py-2 rounded-2xl bg-fuchsia-600 text-white shadow hover:bg-fuchsia-700">+ New Announcement</button>
                </div>

                {items.length===0 ? (
                  <div className="text-slate-400 text-center py-10">No announcements yet.</div>
                ) : (
                  <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
                    {items.map(it=>{
                      const canEdit =
                        currentUser &&
                        it.owner &&
                        currentUser.trim().toLowerCase() === it.owner.trim().toLowerCase();
                      return (
                        <div key={it.id} className="bg-white rounded-3xl shadow ring-1 ring-slate-200 overflow-hidden">
                          {it.image
                            ? <img src={it.image} className="w-full aspect-[4/3] object-cover" alt="" />
                            : <div className="w-full aspect-[4/3] bg-gradient-to-br from-slate-100 to-slate-200" />}
                          <div className="p-6">
                            <div className="text-xs text-slate-400 mb-2">{new Date(it.createdAt).toLocaleString()}</div>
                            <div className="font-extrabold text-2xl leading-tight">{it.title}</div>
                            {it.subtitle && <div className="text-slate-600 mt-1 text-lg">{it.subtitle}</div>}
                            {it.body && <p className="mt-3 text-slate-700 text-[17px] leading-relaxed">{it.body}</p>}
                            <div className="text-[12px] text-slate-400 mt-3">Owner: {it.owner || "unknown"}</div>
                            {canEdit && (
                              <div className="flex gap-2 mt-4">
                                <button className="px-3 py-2 rounded-xl border text-sm" onClick={()=>{ setDef(it); setShow(true); }}>Edit</button>
                                <button className="px-3 py-2 rounded-xl border text-sm text-rose-600 hover:bg-rose-50" onClick={()=>remove(it.id)}>Delete</button>
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}

                {show && <AnnouncementForm defaults={def} onClose={()=>{ setShow(false); setDef(null); }} onSave={save} />}
              </div>
            );
          }

          function AnnouncementForm({ defaults, onClose, onSave }) {
            const [title, setTitle] = useState(defaults?.title || "");
            const [subtitle, setSubtitle] = useState(defaults?.subtitle || "");
            const [body, setBody] = useState(defaults?.body || "");
            const [image, setImage] = useState(defaults?.image || "");
            function handleFile(e){
              const file = e.target.files?.[0]; if(!file) return;
              const reader = new FileReader(); reader.onload = () => setImage(String(reader.result)); reader.readAsDataURL(file);
            }
            return (
              <div className="fixed inset-0 z-30 flex items-center justify-center bg-black/40 p-4">
                <div className="w-full max-w-2xl bg-white rounded-3xl shadow-xl p-6">
                  <div className="flex items-start justify-between">
                    <h3 className="text-2xl font-extrabold">{defaults ? "Edit Announcement" : "New Announcement"}</h3>
                    <button className="px-3 py-2 rounded-xl border text-sm" onClick={onClose}>Close</button>
                  </div>
                  <div className="grid sm:grid-cols-2 gap-4 mt-4">
                    <div className="sm:col-span-2">
                      <label className="block text-xs text-slate-500 mb-1">Title</label>
                      <input value={title} onChange={(e)=>setTitle(e.target.value)} className="w-full px-4 py-3 border rounded-2xl text-lg" />
                    </div>
                    <div className="sm:col-span-2">
                      <label className="block text-xs text-slate-500 mb-1">Subtitle (optional)</label>
                      <input value={subtitle} onChange={(e)=>setSubtitle(e.target.value)} className="w-full px-4 py-3 border rounded-2xl" />
                    </div>
                    <div className="sm:col-span-2">
                      <label className="block text-xs text-slate-500 mb-1">Body</label>
                      <textarea rows={5} value={body} onChange={(e)=>setBody(e.target.value)} className="w-full px-4 py-3 border rounded-2xl" />
                    </div>
                    <div>
                      <label className="block text-xs text-slate-500 mb-1">Photo (optional)</label>
                      <input type="file" accept="image/*" onChange={handleFile} className="w-full" />
                    </div>
                    {image && (<div><div className="text-xs text-slate-500 mb-1">Preview</div><img src={image} className="w-full aspect-[4/3] object-cover rounded-2xl border" /></div>)}
                  </div>
                  <div className="flex justify-end gap-2 mt-5">
                    <button className="px-4 py-2 rounded-2xl border" onClick={onClose}>Cancel</button>
                    <button className="px-4 py-2 rounded-2xl bg-fuchsia-600 text-white" onClick={()=>{
                      if(!title.trim()){ alert("Please add a title."); return; }
                      onSave({
                        id: defaults?.id || crypto.randomUUID(),
                        title: title.trim(),
                        subtitle: subtitle.trim(),
                        body: body.trim(),
                        image: image || "",
                        createdAt: defaults?.createdAt || Date.now(),
                        owner: defaults?.owner // set in save()
                      });
                    }}>Save</button>
                  </div>
                </div>
              </div>
            );
          }

          const root = document.getElementById('root');
          ReactDOM.createRoot(root).render(<App />);
          root.dataset.ok = "1";
        </script>
      </body>
    </html>
    """
    return Response(html, mimetype="text/html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Railway uses 8000
    app.run(host="0.0.0.0", port=port, debug=True)
