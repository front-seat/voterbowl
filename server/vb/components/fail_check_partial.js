function failCheckPartial(self, props) {
  const { schoolName, firstName, lastName } = props;

  let email = null;
  let count = 0; // give up after 3 tries
  while (email === null && count < 3) {
    email = prompt(`Sorry, but we need your ${schoolName} student email to continue. Please enter it below:`);
    count++;
  }

  if (email) {
    htmx.ajax("POST", "./finish/", {
      target: document.querySelector(".urgency"),
      values: {
        email: email,
        first_name: firstName,
        last_name: lastName,
        school: schoolName
      }
    });
  }
}
