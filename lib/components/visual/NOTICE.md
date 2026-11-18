# Notices for the shared visual runtime

Selected Stageshow source is Copyright (c) 2026 Benji Taylor, MIT licensed;
see LICENSE. The pinned upstream revision and original file hashes are in
UPSTREAM.json. Local adaptations are identified there.

This selection excludes the upstream brand registry, BrandMark component,
application icon assets, photographs, and real-product studies. Product and
operating-system names or familiar device geometry mentioned in reference
documentation remain with their owners and do not imply endorsement.

The selected kit and examples use CSS and source-drawn vector shapes. No
third-party fonts or remote photographs are bundled. React, lucide-react and
development dependencies retain their own licenses in their installed packages.

The optional Phone photo frame requires a separately permitted bezel image;
none is bundled. Without one, the kit uses its CSS frame.

The Chinese examples contain fictional demonstration data. They do not show a
working customer system or certify any product capability.

Maintenance now lives in the shared visual resource library. Offline exports retain the pinned upstream version, license and local adaptations.

The local shared-library integration replaces the upstream per-project copy
workflow: consumers reference this runtime directly. All document, diagram,
task-map and product-map UI is now implemented in shared React components;
export uses the same components for SSR and browser hydration.

Live UI composition adapts MIT shadcn/ui Radix components; see ui/SOURCES.json
and ui/licenses/shadcn-ui.txt. Radix UI and its exact dependency closure are
locked in package-lock.json. The exporter embeds package license notices from
the actual browser build along with the shadcn and original Stageshow notices.
The shared-source notices are retained for every export, including scenes that
use kit or adapted examples; they are not inferred from node_modules alone.
Motion Primitives and
Bencho were inspected as references; no paid blocks or their assets are included.
