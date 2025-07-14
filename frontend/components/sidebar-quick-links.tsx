import { Globe, FileText, Phone, Mail, MapPin, Info, ExternalLink } from "lucide-react";
import React from "react";

const quickLinks = [
  {
    category: "Official Portals",
    links: [
      {
        icon: <Globe className="mr-2" />,
        label: "PMAY-U Official Website",
        href: "https://pmaymis.gov.in/",
        description: "Main PMAY Urban portal",
        external: true,
      },
      {
        icon: <Globe className="mr-2" />,
        label: "MoHUA Official Website",
        href: "https://mohua.gov.in/",
        description: "Ministry of Housing & Urban Affairs",
        external: true,
      },
      {
        icon: <Globe className="mr-2" />,
        label: "Digital India Portal",
        href: "https://digitalindia.gov.in/",
        description: "Digital India initiatives",
        external: true,
      },
    ],
  },
  {
    category: "Application & Forms",
    links: [
      {
        icon: <FileText className="mr-2" />,
        label: "Online Application Portal",
        href: "https://pmaymis.gov.in/",
        description: "Apply for PMAY online",
        external: true,
      },
      {
        icon: <FileText className="mr-2" />,
        label: "Application Form Download",
        href: "https://pmaymis.gov.in/",
        description: "Download application forms",
        external: true,
      },
      {
        icon: <FileText className="mr-2" />,
        label: "Document Checklist",
        href: "https://pmaymis.gov.in/",
        description: "Required documents list",
        external: true,
      },
    ],
  },
  {
    category: "Support & Help",
    links: [
      {
        icon: <Phone className="mr-2" />,
        label: "Helpline: 1800-11-6163",
        href: "tel:1800116163",
        description: "Toll-free helpline",
        external: false,
      },
      {
        icon: <Mail className="mr-2" />,
        label: "Email Support",
        href: "mailto:support.pmay@gov.in",
        description: "support.pmay@gov.in",
        external: false,
      },
      {
        icon: <MapPin className="mr-2" />,
        label: "Find Nearest Office",
        href: "https://pmaymis.gov.in/",
        description: "Locate PMAY offices",
        external: true,
      },
    ],
  },
  {
    category: "Resources",
    links: [
      {
        icon: <FileText className="mr-2" />,
        label: "Guidelines & Policies",
        href: "https://pmaymis.gov.in/",
        description: "Official guidelines",
        external: true,
      },
      {
        icon: <Info className="mr-2" />,
        label: "FAQ Section",
        href: "https://pmaymis.gov.in/",
        description: "Frequently asked questions",
        external: true,
      },
      {
        icon: <Globe className="mr-2" />,
        label: "Success Stories",
        href: "https://pmaymis.gov.in/",
        description: "PMAY success stories",
        external: true,
      },
    ],
  },
];

export default function SidebarQuickLinks() {
  return (
    <div className="space-y-4">
      {quickLinks.map((section) => (
        <div key={section.category}>
          <h4 className="text-[11px] font-bold text-blue-100 uppercase mb-1 tracking-wider">{section.category}</h4>
          <div className="space-y-1">
            {section.links.map((link) => (
              <a
                key={link.label}
                href={link.href}
                target={link.external ? "_blank" : undefined}
                rel={link.external ? "noopener noreferrer" : undefined}
                className="flex items-center bg-blue-700 hover:bg-blue-600 transition rounded-lg px-3 py-2 text-blue-100 shadow group"
              >
                {React.cloneElement(link.icon, { className: 'mr-2 h-4 w-4 text-blue-200' })}
                <div className="flex-1">
                  <div className="font-semibold flex items-center text-[14px] text-blue-50">
                    {link.label}
                    {link.external && <ExternalLink className="ml-1 h-3 w-3 opacity-60" />}
                  </div>
                  <div className="text-[11px] text-blue-200 leading-tight">{link.description}</div>
                </div>
              </a>
            ))}
          </div>
        </div>
      ))}
      {/* Emergency Contact Box */}
      <div className="mt-4 p-3 bg-blue-900 rounded-lg shadow border border-blue-700">
        <div className="font-bold text-blue-100 mb-1 text-[12px]">Emergency Contact</div>
        <div className="flex items-center text-blue-100 text-[13px] mb-1">
          <Phone className="mr-2 h-3 w-3 text-blue-200" />
          <a href="tel:1800116163" className="underline hover:text-blue-200">24/7 Helpline: 1800-11-6163</a>
        </div>
        <div className="flex items-center text-blue-100 text-[13px]">
          <Mail className="mr-2 h-3 w-3 text-blue-200" />
          <a href="mailto:pmay.helpdesk@gov.in" className="underline hover:text-blue-200">pmay.helpdesk@gov.in</a>
        </div>
      </div>
    </div>
  );
} 