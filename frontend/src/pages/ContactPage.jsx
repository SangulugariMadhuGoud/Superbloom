import { useRef, useState } from 'react'
import { API_BASE } from '../lib/api'
import { useToast } from '../components/Toast'

const ContactPage = () => {
  const [submitting, setSubmitting] = useState(false)
  const toast = useToast()
  const inFlightRef = useRef(false)

  async function onSubmit(e) {
    e.preventDefault()
    if (inFlightRef.current || submitting) return
    inFlightRef.current = true
    setSubmitting(true)
    const form = new FormData(e.currentTarget)
    const payload = {
      name: form.get('name'),
      email: form.get('email'),
      service: form.get('service') || '',
      message: form.get('message')
    }
    try {
      if (!payload.name || !payload.email || !payload.message) {
        toast.error('Please fill required fields')
        return
      }
      const res = await fetch(`${API_BASE}/api/contact`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      if (!res.ok) {
        toast.error('Could not send. Please try again.')
        return
      }
      // optionally read response
      // const data = await res.json()
      toast.success("Thanks! We'll get back to you shortly.")
      e.currentTarget.reset()
    } catch (err) {
      toast.error('Could not send. Please try again.')
    } finally {
      setSubmitting(false)
      inFlightRef.current = false
    }
  }

  return (
    <main className="pt-24">
      <section className="py-20 text-center">
        <div className="container mx-auto px-6">
          <h1 className="text-5xl md:text-7xl font-black tracking-tighter">
            Let's build something <br />
            <span className="gradient-text">great together.</span>
          </h1>
          <p className="mt-6 text-lg md:text-xl text-gray-400 max-w-3xl mx-auto">
            Have a project in mind? We'd love to hear about it. Fill out the form below or email us
            directly, and we'll get back to you within 24 hours.
          </p>
        </div>
      </section>

      <section className="py-12">
        <div className="container mx-auto px-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
            <div>
              <h2 className="text-3xl font-bold mb-6">Contact Info</h2>
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-semibold gradient-text">Email Us</h3>
                  <p className="text-gray-300 mt-1">Our inbox is always open.</p>
                  <a href="mailto:hello@superbloom.agency" className="text-white hover:underline">hello@superbloom.agency</a>
                </div>
                <div>
                  <h3 className="text-xl font-semibold gradient-text">Our Location</h3>
                  <p className="text-gray-300 mt-1">Hyderabad, Telangana</p>
                  <p className="text-gray-400">India</p>
                </div>
              </div>
            </div>

            <div className="lg:col-span-2">
              <div className="bg-[#111] p-8 rounded-2xl border border-gray-800">
                <form onSubmit={onSubmit}>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label htmlFor="name" className="block text-sm font-medium text-gray-400 mb-2">Full Name</label>
                      <input type="text" id="name" name="name" required className="form-input bg-[#1a1a1a] border border-[#333] rounded-lg py-3 px-4 text-white w-full focus:outline-none focus:border-[#A855F7]" />
                    </div>
                    <div>
                      <label htmlFor="email" className="block text-sm font-medium text-gray-400 mb-2">Email Address</label>
                      <input type="email" id="email" name="email" required className="form-input bg-[#1a1a1a] border border-[#333] rounded-lg py-3 px-4 text-white w-full focus:outline-none focus:border-[#A855F7]" />
                    </div>
                  </div>
                  <div className="mt-6">
                    <label htmlFor="service" className="block text-sm font-medium text-gray-400 mb-2">Service of Interest</label>
                    <select id="service" name="service" className="form-input bg-[#1a1a1a] border border-[#333] rounded-lg py-3 px-4 text-white w-full focus:outline-none focus:border-[#A855F7]">
                      <option>Web Designing</option>
                      <option>UI/UX Designing</option>
                      <option>Custom Web Development</option>
                      <option>E-commerce Websites</option>
                      <option>Content Creation</option>
                      <option>Email Automations</option>
                      <option>Other</option>
                    </select>
                  </div>
                  <div className="mt-6">
                    <label htmlFor="message" className="block text-sm font-medium text-gray-400 mb-2">Tell us about your project</label>
                    <textarea id="message" name="message" rows={5} required className="form-input bg-[#1a1a1a] border border-[#333] rounded-lg py-3 px-4 text-white w-full focus:outline-none focus:border-[#A855F7]" />
                  </div>
                  <div className="mt-8 text-right">
                    <button type="submit" disabled={submitting} className="gradient-bg text-white font-bold py-3 px-8 rounded-full text-lg hover:opacity-90 transition-opacity duration-300 disabled:opacity-50 disabled:cursor-not-allowed">
                      {submitting ? 'Sending...' : 'Send Message'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
};

export default ContactPage;