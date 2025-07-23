import { Globe, FileText, Phone, Mail, MapPin, Info, ExternalLink } from "lucide-react";
import React from "react";
import { TranslationKey } from "@/hooks/use-translation";

const quickLinks = (t: (key: TranslationKey) => string) => [
  {
    category: t('official_portals'),
    links: [
      {
        icon: <Globe className="mr-2" />,
        label: t('pmay_u_website'),
        href: "https://pmaymis.gov.in/PMAYMIS2_2024/PmayDefault.aspx",
        description: t('main_pmay_portal'),
        external: true,
      },
      {
        icon: <Globe className="mr-2" />,
        label: t('mohua_website'),
        href: "https://mohua.gov.in/",
        description: t('ministry_of_housing'),
        external: true,
      },
    ],
  },
  {
    category: t('application_and_forms'),
    links: [
      {
        icon: <FileText className="mr-2" />,
        label: t('online_application_portal'),
        href: "https://pmaymis.gov.in/PMAYMIS2_2024/PMAY_SURVEY/EligiblityCheck.aspx",
        description: t('apply_for_pmay'),
        external: true,
      },
      {
        icon: <MapPin className="mr-2" />, 
        label: t('find_nearest_csc'),
        href: "https://locator.csccloud.in/",
        description: t('locate_csc_centers'),
        external: true,
      },
    ],
  },
  {
    category: t('support_and_help'),
    links: [
      {
        icon: <Phone className="mr-2" />,
        label: t('helpline'),
        href: "tel:1800116163",
        description: t('toll_free_helpline'),
        external: false,
      },
      {
        icon: <Mail className="mr-2" />,
        label: t('email_support'),
        href: "mailto:support.pmay@gov.in",
        description: "support.pmay@gov.in",
        external: false,
      },
    ],
  },
  {
    category: t('resources'),
    links: [
      {
        icon: <FileText className="mr-2" />,
        label: t('guidelines_and_policies'),
        href: "https://pmaymis.gov.in/",
        description: t('official_guidelines'),
        external: true,
      },
      {
        icon: <Info className="mr-2" />,
        label: t('faq_section'),
        href: "https://pmaymis.gov.in/",
        description: t('frequently_asked_questions'),
        external: true,
      },
      {
        icon: <Globe className="mr-2" />,
        label: t('success_stories'),
        href: "https://pmaymis.gov.in/",
        description: t('pmay_success_stories'),
        external: true,
      },
    ],
  },
];

export default function SidebarQuickLinks({ t }: { t: (key: TranslationKey) => string }) {
  const links = quickLinks(t);
  return (
    <div className="space-y-4">
      {links.map((section) => (
        <div key={section.category}>
          <h4 className="text-[11px] font-bold text-blue-100 uppercase mb-1 tracking-wider">{section.category}</h4>
          <div className="space-y-1">
            {section.links.map((link) => (
              <a
                key={link.label}
                href={link.href}
                target={link.external ? "_blank" : undefined}
                rel={link.external ? "noopener noreferrer" : undefined}
                className="flex items-center px-1 py-1 text-blue-100 hover:underline transition group"
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
        <div className="font-bold text-blue-100 mb-1 text-[12px]">{t('emergency_contact')}</div>
        <div className="flex items-center text-blue-100 text-[13px] mb-1">
          <Phone className="mr-2 h-3 w-3 text-blue-200" />
          <a href="tel:1800116163" className="underline hover:text-blue-200">{t('twenty_four_seven_helpline')}</a>
        </div>
        <div className="flex items-center text-blue-100 text-[13px]">
          <Mail className="mr-2 h-3 w-3 text-blue-200" />
          <a href="mailto:pmay.helpdesk@gov.in" className="underline hover:text-blue-200">pmay.helpdesk@gov.in</a>
        </div>
      </div>
    </div>
  );
} 