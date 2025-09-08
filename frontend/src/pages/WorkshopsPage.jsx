import { useEffect, useRef, useState } from 'react'
import { listWorkshops, registerWorkshop } from '../lib/api'
import { useToast } from '../components/Toast'

const WorkshopsPage = () => {
  const toast = useToast()
  const [modalOpen, setModalOpen] = useState(false)
  const [workshops, setWorkshops] = useState([])
  const [activeWs, setActiveWs] = useState(null)
  const fileInputRef = useRef(null)
  const [fileLabel, setFileLabel] = useState('Click here to upload your screenshot')

  async function load() {
    try {
      const data = await listWorkshops()
      setWorkshops(data.items || [])
    } catch (e) {
      toast.error('Failed to load workshops')
    }
  }

  useEffect(() => {
    load()
    const id = setInterval(load, 10000)
    return () => clearInterval(id)
  }, [])

  const soldOut = activeWs ? activeWs.registrations_count >= activeWs.capacity : false
  const percentage = activeWs ? Math.min(100, (activeWs.registrations_count / activeWs.capacity) * 100) : 0

  const activeList = workshops.filter(w => w.status === 'active')
  const inactiveList = workshops.filter(w => w.status === 'inactive')

  return (
    <main className="pt-24">
      <section className="py-24 text-center">
        <div className="container mx-auto px-6">
          <h1 className="text-5xl md:text-7xl font-black tracking-tighter">
            The <span className="gradient-text">Superbloom Lab</span>
          </h1>
          <p className="mt-6 text-lg md:text-xl text-gray-400 max-w-3xl mx-auto">
            We don't just build; we teach. The Lab is our commitment to the tech community—a space
            for workshops, hackathons, and fostering the next generation of talent in Hyderabad.
          </p>
        </div>
      </section>

      <section className="py-12">
        <div className="container mx-auto px-6 space-y-8">
          <h2 className="text-3xl font-bold tracking-tighter mb-2">Upcoming Workshops</h2>
          {activeList.map((ws) => (
            <div key={ws.id} className="bg-[#111] border border-gray-800 rounded-2xl overflow-hidden md:flex">
              <img
                src={ws.image_url || "https://placehold.co/600x400/A855F7/0A0A0A?text=Workshop"}
                alt={ws.title}
                className="w-full md:w-1/3 object-cover"
              />
              <div className="p-8 flex flex-col justify-between">
                <div>
                  <h3 className="text-3xl font-bold">{ws.title}</h3>
                  <p className="text-gray-400 mt-4">{ws.description}</p>
                  <div className="mt-6 grid grid-cols-2 md:grid-cols-3 gap-6 text-sm">
                    <div>
                      <p className="font-semibold text-white">Date</p>
                      <p className="text-gray-400">{ws.date}</p>
                    </div>
                    <div>
                      <p className="font-semibold text-white">Time</p>
                      <p className="text-gray-400">{ws.start_time} - {ws.end_time}</p>
                    </div>
                    <div>
                      <p className="font-semibold text-white">Venue</p>
                      <p className="text-gray-400">{ws.venue}</p>
                    </div>
                    <div className="col-span-2">
                      <p className="font-semibold text-white">Perks</p>
                      <p className="text-gray-400">{ws.perks}</p>
                    </div>
                    <div>
                      <p className="font-semibold text-white">Registrations</p>
                      <p className="text-gray-400">{ws.registrations_count} / {ws.capacity} Registered</p>
                      <div className="w-full bg-gray-700 rounded-full h-2 mt-1">
                        <div
                          className="gradient-bg h-2 rounded-full transition-all duration-500"
                          style={{ width: `${Math.min(100, (ws.registrations_count / ws.capacity) * 100)}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
                <button
                  className={`register-btn mt-8 w-full md:w-auto font-semibold py-3 px-8 rounded-full transition-opacity duration-300 ${
                    ws.is_sold_out ? 'bg-gray-600 cursor-not-allowed opacity-50' : 'gradient-bg text-white hover:opacity-90'
                  }`}
                  onClick={() => { if (!ws.is_sold_out) { setActiveWs(ws); setModalOpen(true) } }}
                  disabled={ws.is_sold_out}
                >
                  {ws.is_sold_out ? 'Sold Out' : 'Register Now'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="py-24">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl font-bold tracking-tighter mb-8">Past Workshops</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {inactiveList.map((ws) => (
              <div key={ws.id} className="bg-[#111] border border-gray-800 rounded-2xl p-6 opacity-80">
                <p className="text-sm font-semibold text-gray-500">{ws.date}</p>
                <h4 className="text-xl font-bold mt-2">{ws.title}</h4>
                <p className="text-gray-400 mt-2 text-sm">{ws.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {modalOpen && activeWs && (
        <div
          className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center p-4 z-50"
          onClick={(e) => {
            if (e.target === e.currentTarget) setModalOpen(false)
          }}
        >
          <div className="bg-[#111] border border-gray-800 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto p-8 relative">
            <button
              className="absolute top-4 right-4 text-gray-500 hover:text-white"
              onClick={() => setModalOpen(false)}
            >
              &times;
            </button>
            <div>
              <h2 className="text-3xl font-bold mb-2">Register for {activeWs.title}</h2>
              <p className="text-gray-400 mb-6">Complete the steps below to secure your spot.</p>

              <form
                onSubmit={async (e) => {
                  e.preventDefault()
                  const fd = new FormData(e.currentTarget)
                  try {
                    await registerWorkshop(activeWs.id, fd)
                    toast.success('Registered!')
                    setModalOpen(false)
                    load()
                  } catch (err) {
                    toast.error('Registration failed')
                  }
                }}
              >
                <h3 className="text-xl font-semibold mb-4 gradient-text">Step 1: Complete Payment</h3>
                <div className="flex flex-col md:flex-row gap-6 items-center bg-[#0A0A0A] p-6 rounded-lg">
                  <img src={activeWs.payment_qr || "https://placehold.co/200x200/ffffff/000000?text=QR"} alt="Payment QR Code" className="w-48 h-48 rounded-lg object-contain bg-white" />
                  <div className="text-center md:text-left">
                    <p className="font-semibold">Scan the QR code or use the details below.</p>
                    <p className="text-gray-400 mt-2"><strong>UPI ID:</strong> {activeWs.upi_id || '—'}</p>
                    <p className="text-gray-400"><strong>Bank:</strong> {activeWs.bank_name || '—'}</p>
                    <p className="text-gray-400"><strong>Account No:</strong> {activeWs.account_no || '—'}</p>
                    <p className="text-2xl font-bold mt-2">Amount: ₹{activeWs.amount || '—'}</p>
                  </div>
                </div>

                <h3 className="text-xl font-semibold mt-8 mb-4 gradient-text">Step 2: Fill Your Details</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <input name="name" type="text" placeholder="Full Name" required className="form-input" />
                  <input name="email" type="email" placeholder="Email Address" required className="form-input" />
                  <input name="whatsapp" type="tel" placeholder="WhatsApp Number" className="form-input" />
                  <input name="organization" type="text" placeholder="College / Company" className="form-input" />
                </div>

                <h3 className="text-xl font-semibold mt-8 mb-4 gradient-text">Step 3: Upload Payment Screenshot</h3>
                <label className="file-input-wrapper">
                  <span className={fileLabel !== 'Click here to upload your screenshot' ? 'gradient-text' : ''}>{fileLabel}</span>
                  <input
                    name="payment_proof"
                    ref={fileInputRef}
                    type="file"
                    accept="image/png, image/jpeg, image/jpg"
                    onChange={(e) => {
                      const file = e.target.files?.[0]
                      setFileLabel(file ? file.name : 'Click here to upload your screenshot')
                    }}
                  />
                </label>

                <button type="submit" className="mt-8 w-full gradient-bg text-white font-semibold py-3 px-8 rounded-full hover:opacity-90 transition-opacity duration-300">
                  Submit Registration
                </button>
              </form>
            </div>
          </div>
        </div>
      )}
    </main>
  )
}

export default WorkshopsPage


