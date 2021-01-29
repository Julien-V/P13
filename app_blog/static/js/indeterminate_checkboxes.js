// Gruidbuilder@https://css-tricks.com/indeterminate-checkboxes/

function onChange({target}) {
	if (target.type !== 'checkbox') {
		return;
	}
	updateChildren(target);
	updateParents(target);
}

function updateChildren(el) {
	const {checked} = el;
	getChildren(el).forEach(child => {
		child.checked = checked;
		child.indeterminate = false;
	} );
}

function updateParents(parent) {
	while (parent=getParent(parent)) {
		let children = getChildren(parent);
		let checked = [...children].filter(child => child.checked).length;
		parent.checked = checked === children.length;
		parent.indeterminate = checked && ! parent.checked;
	}
}

function getChildren(el) {
	el = el.closest('li');
	el = el && el.querySelector('ul');
	return el && el.querySelectorAll('input[type="checkbox"]') || [];
}

function getParent(el) {
	el = el.closest('ul');
	el = el && el.closest('li');
	return el && el.querySelector('input[type="checkbox"]');
}

addEventListener('change', onChange);