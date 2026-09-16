# Folders

Folders are labels, not physical locations. They are stored on each object as `other_config.folder`.

## Convention

- VM folder: `/Prod/Web`
- Network folder: `/Prod/DMZ`
- Nested: `/Prod/Web/Frontend`

## Move a VM into a folder

Select the VM, choose **Set folder**, enter the path. Windows XCP-ng Center reads the same key, so both consoles stay in sync.
