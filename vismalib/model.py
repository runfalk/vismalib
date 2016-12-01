from urlparse import urljoin
from datetime import date, datetime

from .utils import combomethod, AttrProxy

__all__ = [
    "DeliveryTerms",
    "DeliveryMethod",
    "Address",
    "TermsOfPayment",
    "Customer",
]

def coalesce(*args):
    for item in args:
        if item is not None:
            return item


def validate_country_code(code, use_exceptions=True):
    try:
        if len(code) != 2:
            raise ValueError("Country code '{}' is not 2 characters".format(code))

        if code.upper() != code:
            raise ValueError("Country code '{}' is not uppercase".format(code))
    except Exception as e:
        if use_exceptions:
            raise e
        return False
    else:
        return True


class ModelReprMixin(object):
    __slots__ = ()

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join(
                "{}={!r}".format(attr, getattr(self, attr))
                for attr in self.__slots__ if getattr(self, attr) is not None))


class VismaModel(object):
    __slots__ = ()

    __visma_path__ = None
    __visma_key__ = None
    __visma_methods__ = frozenset()
    __visma_version__ = "v1"

    @classmethod
    def has_support(cls, method):
        return method in cls.__visma_methods__

    @combomethod
    def from_json(cls, self, json):
        """
        Create a new object from a JSON response.

        :param json: Deserialized JSON data from an API call
        :return: New object
        :rtype: Customer
        """

        raise NotImplementedError(
            "from_json is not implemented for {}".format(cls.__name__))

    def from_json(self):
        """
        Convert object to a dict that is ready to be serialized to JSON.

        :return: Visma formatted dictionary
        :rtype: dict
        """

        raise NotImplementedError(
            "to_json is not implemented for {}".format(self.__class__.__name__))

    @classmethod
    def _visma_get_path(cls, *args):
        if cls.__visma_path__ is None:
            raise ValueError(
                "__visma_path__ is not defined for {}".format(
                    cls.__name__))

        return "/".join(str(arg) for arg in (cls.__visma_path__,) + args)

    @classmethod
    def _visma_list(cls, **kwargs):
        if not cls.has_support("list"):
            raise NotImplementedError(
                "Listing of {} is not supported".format(cls.__name__))

        return {
            "method": "GET",
            "url": cls._visma_get_path(),
            "data": kwargs,
        }

    @classmethod
    def _visma_get(cls, id):
        if not cls.has_support("get"):
            raise NotImplementedError(
                "Getting {} is not supported".format(cls.__name__))

        if cls.__visma_path__ is None:
            raise ValueError(
                "__visma_path__ is not defined for {}".format(
                    cls.__name__))

        return {
            "method": "GET",
            "url": cls._visma_get_path(id),
        }

    def _visma_add(self):
        if not self.has_support("add"):
            raise NotImplementedError(
                "Adding {} is not supported".format(self.__class__.__name__))

        if self.__visma_path__ is None:
            raise ValueError(
                "__visma_path__ is not defined for {}".format(
                    self.__class__.__name__))

        return {
            "method": "POST",
            "url": self._visma_get_path(),
            "json": self.to_json(),
        }

    def _visma_update(self):
        if not self.has_support("update"):
            raise NotImplementedError(
                "Updating {} is not supported".format(self.__class__.__name__))

        if self.__visma_key__ is None:
            raise ValueError(
                "__visma_key__ is not defined for {}".format(
                    self.__class__.__name__))

        return {
            "method": "PUT",
            "url": self._visma_get_path(getattr(self, self.__visma_key__)),
            "json": self.to_json(),
        }

    def _visma_remove(self):
        if not self.has_support("remove"):
            raise NotImplementedError(
                "Removing {} is not supported".format(self.__class__.__name__))

        return {
            "method": "DELETE",
            "url": self._visma_get_path(getattr(self, self.__visma_key__)),
        }

class DeliveryBase(ModelReprMixin):
    __slots__ = ("id", "code", "name")

    def __init__(self, id=None, code=None, name=None):
        self.id = id
        self.code = code
        self.name = name

    @combomethod
    def from_json(cls, self, json):
        if self is None:
            self = cls()

        self.id = json.get("Id")
        self.code = json.get("Code")
        self.name = json.get("Name")

        return self


class DeliveryTerms(DeliveryBase):
    pass


class DeliveryMethod(DeliveryBase):
    pass


class Address(ModelReprMixin):
    """
    Abstraction of address fields

    :param name: Address name
    :param address: Primary address line
    :param secondary_address: Secondary address line
    :param postal_code: Postal code
    :param city: City
    :param country: Two letter country code.
    """

    __slots__ = (
        "name",
        "address",
        "secondary_address",
        "postal_code",
        "city",
        "country",
    )

    def __init__(
            self, name=None, address=None, secondary_address=None,
            postal_code=None, city=None, country=None):
        self.name = name
        self.address = address
        self.secondary_address = secondary_address
        self.postal_code = postal_code
        self.city = city
        self.country = country

        if address is not None:
            validate_country_code(country)

    def __bool__(self):
        # Address objects are considered empty when they only contain None
        return not (
            self.name is None and
            self.address is None and
            self.secondary_address is None and
            self.postal_code is None and
            self.city is None and
            self.country is None)

    # Python 2 compatibility
    __nonzero__ = __bool__


class TermsOfPayment(ModelReprMixin):
    __slots__ = (
        "id",
        "name",
        "english_name",
        "days",
        "type_id",
        "type_text",
    )

    def __init__(
            self, id=None, name=None, english_name=None, days=None, type_id=None,
            type_text=None):
        self.id = id
        self.name = name
        self.english_name = english_name
        self.days = days
        self.type_id = type_id
        self.type_text = type_text

    @combomethod
    def from_json(cls, self, json):
        if self is None:
            self = cls()

        self.id = json.get("Id")
        self.name = json.get("Name")
        self.english_name = json.get("NameEnglish")
        self.days = json.get("NumberOfDays")
        self.type_id = json.get("TermsOfPaymentId")
        self.type_text = json.get("TermsOfPaymentTypeText")

        return self


class Customer(ModelReprMixin, VismaModel):
    """
    Representation of a customer.

    :param id: Visma ID number for customer (read-only)
    :param number:
    :param nin: National identity number
    :param is_company: True if customer is a company, else False
    :param name: Short-hand for setting name of address field (proxy)
    :param vat_number: VAT number
    :param currency: Three letter currency code
    :param gln: Global Location Number
    :param email: E-mail where invoices are sent
    :param phone: Phone number
    :param mobile_phone: Mobile phone number
    :param url: Homepage
    :param note: Free text note
    :param contact_name: Contact person name
    :param contact_email: Contact person e-mail
    :param contact_phone: Contact person phone number
    :param contact_mobile_phone: Contact person phone number
    :param address: Address object containing customer address
    :param delivery_address: Address containing an alternative delivery address
    :param delivery_method: DeliveryMethod object
    :param delivery_terms: DeliveryTerms object
    :param terms_of_payment: TermsOfPayment object
    :param webshop_customer_number: Webshop customer number
    :param last_invoice_date: Last invoice sent (UTC)
    :param last_edited: Last time edited (UTC)
    :param reverse_charge_on_construction_services: Unknown
    """

    __visma_path__ = "customers"
    __visma_methods__ = frozenset(["get", "add", "update"])

    __slots__ = (
        "id",
        "number",
        "nin",
        "is_company",
        "vat_number",
        "currency",
        "gln",
        "email",
        "phone",
        "mobile_phone",
        "url",
        "note",

        "contact_name",
        "contact_email",
        "contact_phone",
        "contact_mobile_phone",

        "address",
        "delivery_address",
        "delivery_method",
        "delivery_terms",
        "terms_of_payment",

        "webshop_customer_number",
        "last_invoice_date",
        "last_edited",
        "reverse_charge_on_construction_services",
    )

    #: Convenience property for accessing customer name
    name = AttrProxy("address.name")

    def __init__(
            self, id=None, number=None, nin=None, is_company=None, name=None,
            vat_number=None, currency=None, gln=None, email=None, phone=None,
            mobile_phone=None, url=None, note=None, contact_name=None,
            contact_email=None, contact_phone=None, contact_mobile_phone=None,
            address=None, delivery_address=None, delivery_method=None,
            delivery_terms=None, terms_of_payment=None,
            webshop_customer_number=None, last_invoice_date=None,
            last_edited=None, reverse_charge_on_construction_services=None):
        self.id = id
        self.number = number
        self.nin = nin
        self.is_company = is_company
        self.vat_number = vat_number
        self.currency = currency
        self.gln = gln
        self.email = email
        self.phone = phone
        self.mobile_phone = mobile_phone
        self.url = url
        self.note = note

        self.contact_name = contact_name
        self.contact_email = contact_email
        self.contact_phone = contact_phone
        self.contact_mobile_phone = contact_mobile_phone

        self.address = Address() if address is None else address
        self.delivery_address = delivery_address
        self.delivery_method = delivery_method
        self.delivery_terms = delivery_terms
        self.terms_of_payment = terms_of_payment

        self.webshop_customer_number = webshop_customer_number
        self.last_invoice_date = last_invoice_date
        self.last_edited = last_edited
        self.reverse_charge_on_construction_services = reverse_charge_on_construction_services

        if name is not None:
            self.name = name

    def to_json(self):
        """
        Convert Customer to a dict that is ready to be serialized to JSON.

        :return: Visma formatted dictionary
        :rtype: dict
        """

        return {}

    @combomethod
    def from_json(cls, self, json):
        """
        Create a new Customer object from a JSON response.

        :param json: Deserialized JSON data from an API call
        :return: New customer object
        :rtype: Customer
        """

        # Create a fresh instance if we are calling this as a classmethod,
        # otherwise work on self
        if self is None:
            self = cls()

        # Create a new delivery address
        delivery_address = Address(
            name=json.get("DeliveryCustomerName"),
            address=json.get("DeliveryAddress1"),
            secondary_address=json.get("DeliveryAddress2"),
            postal_code=json.get("DeliveryPostalCode"),
            city=json.get("DeliveryCity"),
            country=json.get("DeliveryCountryCode"))

        delivery_method = None
        if json.get("DeliveryMethodId"):
            delivery_method = DeliveryMethod(id=json.get("DeliveryMethodId"))

        delivery_terms = None
        if json.get("DeliveryTermId"):
            delivery_terms = DeliveryTerms(id=json.get("DeliveryTermId"))

        terms_of_payment = None
        if json.get("TermsOfPaymentId"):
            if self.terms_of_payment is None:
                self.terms_of_payment = TermsOfPayment()
            self.terms_of_payment.from_json(json.get("TermsOfPayment"))

        last_invoice_date = None
        if json.get("LastInvoiceDate") is not None:
            print json.get("LastInvoiceDate")
            last_invoice_date = datetime.strptime(
                json.get("LastInvoiceDate")[:-1], "%Y-%m-%dT%H:%M:%S.%f")

        last_edited = None
        if json.get("ChangedUtc") is not None:
            print json.get("ChangedUtc")
            last_edited = datetime.strptime(
                json.get("ChangedUtc")[:-1], "%Y-%m-%dT%H:%M:%S.%f")

        self.id = json.get("Id")
        self.number = json.get("CustomerNumber")
        self.nin = json.get("CorporateIdentityNumber") or None
        self.is_company = coalesce(json.get("IsPrivatePerson"), True)
        self.vat_number = json.get("VatNumber") or None
        self.currency = json.get("CurrencyCode")
        self.gln = json.get("GLN") or None
        self.email = json.get("EmailAddress") or None
        self.phone = json.get("Phone") or None
        self.mobile_phone = json.get("MobilePhone") or None
        self.url = json.get("WwwAddress") or None
        self.note = json.get("Note") or None
        self.contact_name = json.get("ContactPersonName") or None
        self.contact_email = json.get("ContactPersonEmail") or None
        self.contact_mobile_phone = json.get("ContactPersonMobile") or None
        self.contact_phone = json.get("ContactPersonPhone") or None
        self.address.name = json.get("Name")
        self.address.address = json.get("InvoiceAddress1")
        self.address.secondary_address = json.get("InvoiceAddress2")
        self.address.postal_code = json.get("InvoicePostalCode")
        self.address.city = json.get("InvoiceCity")
        self.address.country = json.get("InvoiceCountryCode")
        self.delivery_address = delivery_address or None
        self.delivery_method = delivery_method
        self.delivery_terms = delivery_terms
        self.terms_of_payment = terms_of_payment
        self.webshop_customer_number = json.get("WebshopCustomerNumber") or None
        self.last_invoice_date = last_invoice_date
        self.last_edited = last_edited
        self.reverse_charge_on_construction_services = json.get("ReverseChargeOnConstructionServices")

        return self
