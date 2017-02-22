# Confrontiv

App to send out inquiries and gather feedback.

## Steps

Follow these steps in the admin.

1. Create a recipient group
2. Go to recipient list and upload a CSV file with these columns:

  - `name` - the name of the recipient
  - `slug` (optional) - identifier of the recipient, may be generated from name
  - `email` (optional)
  - `fax` (optional)
  - `address` (optional)
  - `group` (optional) - slug of group this recipient should be added to

  Your recipient are then created.
3. In the admin create an inquiry template with these attributes
  - Name: the name of the template
  - Subject: the subject of the email and heading on the input page
  - Body: body of the email, should also contain full footer
  - Intro: Markdown of text that will appear on input page
  - Form: JSON definition of form fields, definition further down.

  Subject, Body and Intro may contain Django Template variables.
  Look further down for a details on rendering.
4. Create an inquiry and select a recipient group and a template.
5. Go to the inquiry admin page and upload a CSV with the following fields:
 - `recipient` - the recipient slug as above (you can export recipients as CSV to get tot the slugs)
 - `data` - JSON (yes, JSON in CSV) that contains context for this recipient and this inquiry.
6. Inquiry requests are now created. Their subject, body and intro fields are rendered based on the combined context from the inquiry template and the uploaded recipient data.
You can still adjust them.
7. Use the command line to send these requests out.
  ```shell
  python manage.py confrontiv_send_mail <inquiry_id>
  ```
8. Answers are collected as inquiry responses. You can export them as CSV.

## Template rendering

Subject, Body and Intro are rendered with Django's Template rendering engine. The following dictionaries are combined into one context (keys of later dictionaries overwrite previous keys).

 - Inquiry template form dictionary
 - Dictionary with one key `url` that represents the full URL to the inquiry page
 - The inquiry request context

### Example of a body template

> Dear Sir or Madam,
>
> We have the following record on file: {{ some_value }}.
>
> Please use the following URL to send your statement:
>
> {{ url }}
>
> Kind regards
> Correctiv

### Example of an intro template

> We have the following record on file: {{ some_value }}.
>
> Please use the form below to give us feedback.

## Form definition

The inquiry template form field defines a JSON form definition.
There's a top level `fields` key that is an array of objects.

A field object has a `name` (like in Django forms) and a `type` that needs to be one of these values:
 - `char`: a char field represented by an input field
 - `text`: a textarea
 - `boolean`: a checkbox
 - `choice`: a choice field represented by a select

Any other keys in the field object are given to the field constructor as keyword arguments.

These additional arguments may be important:
 - `label` for a human readable label
 - `required` as a boolean true or false.
 - `help_text` may be helpful

### Example
```json
{"type": "boolean", "name": "is_correct", "label": "Is the data correct?", "required": false}
```

Without `"required": false` the checkbox would need to be checked in order to submit a valid form!
